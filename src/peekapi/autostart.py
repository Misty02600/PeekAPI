"""Windows 当前用户登录自启管理。"""

from __future__ import annotations

import ctypes
import locale
import ntpath
import os
import subprocess
import sys
import threading
import winreg
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from .constants import APP_ID

_RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_VALUE_NAME = APP_ID
_LEGACY_TASK_NAME = rf"\{APP_ID}"
_EXECUTABLE_NAME = "peekapi.exe"
_COMMAND_TIMEOUT_SECONDS = 10
_NO_WINDOW = subprocess.CREATE_NO_WINDOW
_mutation_lock = threading.Lock()

_RegistryData = int | str | list[str] | bytes | None


class AutostartError(RuntimeError):
    """登录自启查询或修改失败。"""


@dataclass(frozen=True)
class _RegistryValue:
    value: _RegistryData
    value_type: int


def is_packaged_app() -> bool:
    return sys.platform == "win32" and bool(getattr(sys, "frozen", False))


def is_autostart_enabled() -> bool:
    """查询当前打包程序是否是实际登记的登录自启目标。

    Returns:
        当前用户 Run 注册项是否以 `REG_SZ` 精确指向正在运行的
        `peekapi.exe`。开发模式、缺少注册项或旧目录路径均返回 `False`。

    Raises:
        AutostartError: 注册表无法读取时抛出。
    """
    if not is_packaged_app():
        return False

    registered = _read_run_value()
    if registered is None or registered.value_type != winreg.REG_SZ:
        return False
    if not isinstance(registered.value, str):
        return False

    executable = _parse_registered_executable(registered.value)
    return executable is not None and _same_windows_path(executable, sys.executable)


def enable_autostart() -> bool:
    """为当前打包程序启用登录自启并迁移同源旧计划任务。

    迁移先写入并回读验证 HKCU Run，再删除确认属于 PeekAPI 的旧任务。
    删除失败时恢复原注册表值，确保失败不会同时丢失两个启动入口。

    Returns:
        是否成功迁移了旧的 `\\PeekAPI` 计划任务。

    Raises:
        AutostartError: 开发模式调用、现有定义归属不明或系统操作失败时抛出。
    """
    executable = _require_packaged_executable()
    command = _format_run_command(executable)

    with _mutation_lock:
        previous = _read_run_value()
        _ensure_registry_value_is_owned(previous)

        legacy_command = _query_legacy_task_command()
        if legacy_command is not None and not _is_peekapi_command(legacy_command):
            raise AutostartError(
                f"计划任务 {_LEGACY_TASK_NAME} 不属于 PeekAPI，已拒绝迁移"
            )

        try:
            _set_run_value(_RegistryValue(command, winreg.REG_SZ))
            _verify_run_value(command)
        except AutostartError as error:
            _raise_after_rollback(previous, error)

        if legacy_command is None:
            return False

        try:
            _delete_legacy_task()
        except AutostartError as error:
            _raise_after_rollback(previous, error)
        return True


def disable_autostart() -> bool:
    """删除明确属于 PeekAPI 的当前用户登录自启注册项。

    Returns:
        是否删除了已存在的注册项。当前运行进程不会退出。

    Raises:
        AutostartError: 注册项归属不明或系统操作失败时抛出。
    """
    with _mutation_lock:
        previous = _read_run_value()
        if previous is None:
            return False
        _ensure_registry_value_is_owned(previous)

        try:
            _delete_run_value()
            if _read_run_value() is not None:
                raise AutostartError("删除 PeekAPI 登录自启注册项后验证失败")
        except AutostartError as error:
            _raise_after_rollback(previous, error)
        return True


def _require_packaged_executable() -> Path:
    if not is_packaged_app():
        raise AutostartError("开发模式不能启用登录自启，请使用打包后的 peekapi.exe")

    executable = Path(sys.executable)
    if executable.name.casefold() != _EXECUTABLE_NAME:
        raise AutostartError(f"当前打包程序不是 {_EXECUTABLE_NAME}，已拒绝注册")
    return executable


def _format_run_command(executable: Path) -> str:
    return f'"{executable}"'


def _read_run_value() -> _RegistryValue | None:
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY_PATH,
            0,
            winreg.KEY_QUERY_VALUE,
        ) as key:
            value, value_type = winreg.QueryValueEx(key, _RUN_VALUE_NAME)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise AutostartError(f"读取 PeekAPI 登录自启注册项失败: {error}") from error
    return _RegistryValue(value, value_type)


def _set_run_value(registered: _RegistryValue) -> None:
    try:
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(
                key,
                _RUN_VALUE_NAME,
                0,
                registered.value_type,
                registered.value,
            )
    except OSError as error:
        raise AutostartError(f"写入 PeekAPI 登录自启注册项失败: {error}") from error


def _delete_run_value() -> None:
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, _RUN_VALUE_NAME)
    except FileNotFoundError:
        return
    except OSError as error:
        raise AutostartError(f"删除 PeekAPI 登录自启注册项失败: {error}") from error


def _verify_run_value(expected_command: str) -> None:
    actual = _read_run_value()
    if actual != _RegistryValue(expected_command, winreg.REG_SZ):
        raise AutostartError("写入 PeekAPI 登录自启注册项后验证失败")


def _restore_run_value(previous: _RegistryValue | None) -> None:
    if previous is None:
        _delete_run_value()
    else:
        _set_run_value(previous)


def _raise_after_rollback(
    previous: _RegistryValue | None, error: AutostartError
) -> None:
    try:
        _restore_run_value(previous)
    except AutostartError as rollback_error:
        raise AutostartError(
            f"{error}；恢复原登录自启注册项也失败: {rollback_error}"
        ) from error
    raise error


def _ensure_registry_value_is_owned(registered: _RegistryValue | None) -> None:
    if registered is None:
        return
    if (
        registered.value_type != winreg.REG_SZ
        or not isinstance(registered.value, str)
        or not _is_peekapi_command(registered.value)
    ):
        raise AutostartError(
            f"注册表值 {_RUN_VALUE_NAME} 不属于 PeekAPI，已拒绝覆盖或删除"
        )


def _parse_registered_executable(command: str) -> str | None:
    command = command.strip()
    if not command:
        return None

    if command.startswith('"'):
        closing_quote = command.find('"', 1)
        if closing_quote <= 1 or command[closing_quote + 1 :].strip():
            return None
        executable = command[1:closing_quote]
    else:
        if '"' in command:
            return None
        executable = command

    if not executable.casefold().endswith(".exe"):
        return None
    return os.path.expandvars(executable)


def _is_peekapi_command(command: str) -> bool:
    executable = _parse_registered_executable(command)
    return (
        executable is not None
        and ntpath.basename(executable).casefold() == _EXECUTABLE_NAME
    )


def _same_windows_path(left: str, right: str) -> bool:
    return ntpath.normcase(ntpath.normpath(left)) == ntpath.normcase(
        ntpath.normpath(right)
    )


def _query_legacy_task_command() -> str | None:
    result = _run_schtasks(["/Query", "/TN", _LEGACY_TASK_NAME, "/XML"])
    if result.returncode != 0:
        if _is_task_not_found(result):
            return None
        detail = (result.stderr or result.stdout).strip() or "未知错误"
        raise AutostartError(f"无法确认计划任务 {_LEGACY_TASK_NAME}: {detail}")

    try:
        root = ET.fromstring(result.stdout)
    except ET.ParseError as error:
        raise AutostartError(
            f"计划任务 {_LEGACY_TASK_NAME} 的 XML 无法解析: {error}"
        ) from error

    commands = root.findall(".//{*}Actions/{*}Exec/{*}Command")
    if len(commands) != 1 or not commands[0].text:
        raise AutostartError(
            f"计划任务 {_LEGACY_TASK_NAME} 不是单一可执行文件动作，已拒绝迁移"
        )
    return commands[0].text.strip()


def _delete_legacy_task() -> None:
    result = _run_schtasks(["/Delete", "/TN", _LEGACY_TASK_NAME, "/F"])
    if result.returncode == 0:
        return

    try:
        if _query_legacy_task_command() is None:
            return
    except AutostartError:
        detail = (result.stderr or result.stdout).strip() or "未知错误"
        raise AutostartError(
            f"删除计划任务 {_LEGACY_TASK_NAME} 失败且无法确认任务状态: {detail}"
        ) from None

    _delete_legacy_task_elevated()

    try:
        legacy_command = _query_legacy_task_command()
    except AutostartError as error:
        raise AutostartError(
            f"以管理员权限删除计划任务 {_LEGACY_TASK_NAME} 后无法确认任务状态"
        ) from error
    if legacy_command is not None:
        raise AutostartError(
            f"以管理员权限删除计划任务 {_LEGACY_TASK_NAME} 后任务仍然存在"
        )


def _delete_legacy_task_elevated() -> None:
    script = (
        "$ErrorActionPreference = 'Stop'; "
        "try { "
        "$process = Start-Process -FilePath 'schtasks.exe' "
        f"-ArgumentList @('/Delete','/TN','{_LEGACY_TASK_NAME}','/F') "
        "-Verb RunAs -WindowStyle Hidden -Wait -PassThru -ErrorAction Stop; "
        "exit $process.ExitCode "
        "} catch { Write-Error $_.Exception.Message; exit 1 }"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            encoding=locale.getencoding(),
            errors="replace",
            timeout=60,
            creationflags=_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AutostartError(f"请求管理员权限删除旧计划任务失败: {error}") from error

    if result.returncode == 0:
        return

    detail = (result.stderr or result.stdout).strip() or "未知错误"
    raise AutostartError(
        f"未能以管理员权限删除计划任务 {_LEGACY_TASK_NAME}，可能已取消 UAC: {detail}"
    )


def _run_schtasks(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["schtasks.exe", *arguments],
            capture_output=True,
            text=True,
            encoding=locale.getencoding(),
            errors="replace",
            timeout=_COMMAND_TIMEOUT_SECONDS,
            creationflags=_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AutostartError(f"执行 schtasks.exe 失败: {error}") from error


def _is_task_not_found(result: subprocess.CompletedProcess[str]) -> bool:
    detail = (result.stderr or result.stdout).casefold()
    messages = {
        ctypes.FormatError(2).strip().rstrip(".。").casefold(),
        "the system cannot find the file specified",
    }
    normalized_detail = detail.replace("。", ".")
    return any(message.replace("。", ".") in normalized_detail for message in messages)
