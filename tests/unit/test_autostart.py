"""Windows 登录自启管理测试。"""

import subprocess
from unittest.mock import MagicMock

import pytest

from peekapi import autostart


@pytest.fixture
def packaged_app(monkeypatch, tmp_path):
    executable = tmp_path / "peekapi.exe"
    monkeypatch.setattr(autostart.sys, "platform", "win32")
    monkeypatch.setattr(autostart.sys, "frozen", True, raising=False)
    monkeypatch.setattr(autostart.sys, "executable", str(executable))
    return executable


@pytest.fixture
def registry(monkeypatch):
    state: dict[str, autostart._RegistryValue | None] = {"value": None}

    def read():
        return state["value"]

    def write(value):
        state["value"] = value

    def delete():
        state["value"] = None

    monkeypatch.setattr(autostart, "_read_run_value", read)
    monkeypatch.setattr(autostart, "_set_run_value", write)
    monkeypatch.setattr(autostart, "_delete_run_value", delete)
    return state


def _registered(command: str) -> autostart._RegistryValue:
    return autostart._RegistryValue(command, autostart.winreg.REG_SZ)


def test_development_mode_rejects_enable(monkeypatch):
    monkeypatch.setattr(autostart.sys, "frozen", False, raising=False)
    read = MagicMock()
    monkeypatch.setattr(autostart, "_read_run_value", read)

    with pytest.raises(autostart.AutostartError, match="开发模式"):
        autostart.enable_autostart()

    read.assert_not_called()


def test_status_requires_current_executable(packaged_app, registry):
    registry["value"] = _registered(f'"{packaged_app}"')
    assert autostart.is_autostart_enabled() is True

    registry["value"] = _registered(r'"D:\Old\peekapi.exe"')
    assert autostart.is_autostart_enabled() is False

    registry["value"] = None
    assert autostart.is_autostart_enabled() is False


def test_first_enable_writes_current_executable(monkeypatch, packaged_app, registry):
    monkeypatch.setattr(autostart, "_query_legacy_task_command", lambda: None)
    delete_task = MagicMock()
    monkeypatch.setattr(autostart, "_delete_legacy_task", delete_task)

    migrated = autostart.enable_autostart()

    assert migrated is False
    assert registry["value"] == _registered(f'"{packaged_app}"')
    delete_task.assert_not_called()


def test_repeated_enable_updates_owned_old_path(monkeypatch, packaged_app, registry):
    registry["value"] = _registered(r'"D:\Old\peekapi.exe"')
    monkeypatch.setattr(autostart, "_query_legacy_task_command", lambda: None)

    autostart.enable_autostart()

    assert registry["value"] == _registered(f'"{packaged_app}"')


def test_enable_refuses_unowned_registry_value(monkeypatch, packaged_app, registry):
    registry["value"] = _registered(r'"D:\Other\other.exe"')
    query_task = MagicMock()
    monkeypatch.setattr(autostart, "_query_legacy_task_command", query_task)

    with pytest.raises(autostart.AutostartError, match="不属于 PeekAPI"):
        autostart.enable_autostart()

    assert registry["value"] == _registered(r'"D:\Other\other.exe"')
    query_task.assert_not_called()


def test_enable_migrates_owned_legacy_task_after_registry_verification(
    monkeypatch, packaged_app
):
    events: list[str] = []
    state: dict[str, autostart._RegistryValue | None] = {"value": None}

    def read():
        events.append("read")
        return state["value"]

    def write(value):
        events.append("write")
        state["value"] = value

    def delete_task():
        events.append("delete-task")

    monkeypatch.setattr(autostart, "_read_run_value", read)
    monkeypatch.setattr(autostart, "_set_run_value", write)
    monkeypatch.setattr(autostart, "_delete_run_value", lambda: None)
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Old\peekapi.exe",
    )
    monkeypatch.setattr(autostart, "_delete_legacy_task", delete_task)

    assert autostart.enable_autostart() is True

    assert state["value"] == _registered(f'"{packaged_app}"')
    assert events == ["read", "write", "read", "delete-task"]


def test_enable_refuses_unowned_legacy_task(monkeypatch, packaged_app, registry):
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Other\other.exe",
    )
    delete_task = MagicMock()
    monkeypatch.setattr(autostart, "_delete_legacy_task", delete_task)

    with pytest.raises(autostart.AutostartError, match="不属于 PeekAPI"):
        autostart.enable_autostart()

    assert registry["value"] is None
    delete_task.assert_not_called()


def test_delete_task_failure_rolls_back_registry(monkeypatch, packaged_app, registry):
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Old\peekapi.exe",
    )

    def fail_delete():
        raise autostart.AutostartError("delete failed")

    monkeypatch.setattr(autostart, "_delete_legacy_task", fail_delete)

    with pytest.raises(autostart.AutostartError, match="delete failed"):
        autostart.enable_autostart()

    assert registry["value"] is None


def test_registry_write_failure_keeps_legacy_task(monkeypatch, packaged_app, registry):
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Old\peekapi.exe",
    )
    delete_task = MagicMock()
    monkeypatch.setattr(autostart, "_delete_legacy_task", delete_task)

    def fail_write(_value):
        raise autostart.AutostartError("write failed")

    monkeypatch.setattr(autostart, "_set_run_value", fail_write)

    with pytest.raises(autostart.AutostartError, match="write failed"):
        autostart.enable_autostart()

    assert registry["value"] is None
    delete_task.assert_not_called()


def test_disable_deletes_only_owned_value(packaged_app, registry):
    registry["value"] = _registered(f'"{packaged_app}"')

    assert autostart.disable_autostart() is True
    assert registry["value"] is None
    assert autostart.disable_autostart() is False


def test_disable_refuses_unowned_value(packaged_app, registry):
    registry["value"] = _registered(r'"D:\Other\other.exe"')

    with pytest.raises(autostart.AutostartError, match="不属于 PeekAPI"):
        autostart.disable_autostart()

    assert registry["value"] == _registered(r'"D:\Other\other.exe"')


def test_query_legacy_task_parses_single_exec_action(monkeypatch):
    xml = """<?xml version="1.0" encoding="UTF-16"?>
    <Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <Actions><Exec><Command>D:\\PeekAPI\\peekapi.exe</Command></Exec></Actions>
    </Task>
    """
    result = subprocess.CompletedProcess([], 0, stdout=xml, stderr="")
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)

    assert autostart._query_legacy_task_command() == r"D:\PeekAPI\peekapi.exe"


def test_query_legacy_task_distinguishes_absent_from_unreadable(monkeypatch):
    result = subprocess.CompletedProcess(
        [], 1, stdout="", stderr=f"ERROR: {autostart.ctypes.FormatError(2)}"
    )
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)
    assert autostart._query_legacy_task_command() is None

    result.stderr = "ERROR: query failed"
    with pytest.raises(autostart.AutostartError, match="无法确认计划任务"):
        autostart._query_legacy_task_command()


def test_query_legacy_task_rejects_multiple_actions(monkeypatch):
    xml = """<Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <Actions>
        <Exec><Command>D:\\PeekAPI\\peekapi.exe</Command></Exec>
        <Exec><Command>D:\\Other\\other.exe</Command></Exec>
      </Actions>
    </Task>"""
    result = subprocess.CompletedProcess([], 0, stdout=xml, stderr="")
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)

    with pytest.raises(autostart.AutostartError, match="单一可执行文件动作"):
        autostart._query_legacy_task_command()


def test_delete_legacy_task_retries_with_elevation(monkeypatch):
    result = subprocess.CompletedProcess(
        [], 1, stdout="", stderr="ERROR: access denied"
    )
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)
    query_task = MagicMock(side_effect=[r"D:\Old\peekapi.exe", None])
    monkeypatch.setattr(autostart, "_query_legacy_task_command", query_task)
    elevated_delete = MagicMock()
    monkeypatch.setattr(autostart, "_delete_legacy_task_elevated", elevated_delete)

    autostart._delete_legacy_task()

    elevated_delete.assert_called_once_with()
    assert query_task.call_count == 2


def test_delete_legacy_task_rejects_unverified_elevated_deletion(monkeypatch):
    result = subprocess.CompletedProcess(
        [], 1, stdout="", stderr="ERROR: access denied"
    )
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Old\peekapi.exe",
    )
    monkeypatch.setattr(autostart, "_delete_legacy_task_elevated", lambda: None)

    with pytest.raises(autostart.AutostartError, match="任务仍然存在"):
        autostart._delete_legacy_task()


def test_delete_legacy_task_propagates_cancelled_elevation(monkeypatch):
    result = subprocess.CompletedProcess(
        [], 1, stdout="", stderr="ERROR: access denied"
    )
    monkeypatch.setattr(autostart, "_run_schtasks", lambda _arguments: result)
    monkeypatch.setattr(
        autostart,
        "_query_legacy_task_command",
        lambda: r"D:\Old\peekapi.exe",
    )

    def cancel_elevation():
        raise autostart.AutostartError("cancelled UAC")

    monkeypatch.setattr(autostart, "_delete_legacy_task_elevated", cancel_elevation)

    with pytest.raises(autostart.AutostartError, match="cancelled UAC"):
        autostart._delete_legacy_task()
