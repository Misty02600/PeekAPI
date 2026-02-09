"""系统信息获取模块

使用 PowerShell 查询 Windows WMI 获取硬件信息。
"""

import json
import socket
import subprocess
from typing import TypedDict

from .logging import logger


class SystemInfo(TypedDict):
    """系统信息类型"""

    hostname: str
    computer_model: str
    motherboard: str
    cpu: str
    gpus: list[str]


def _run_powershell(command: str) -> dict | list | None:
    """执行 PowerShell 命令并返回 JSON 解析结果"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        logger.warning(f"PowerShell 命令执行失败: {e}")
    return None


def _get_computer_model() -> str:
    """获取电脑型号"""
    data = _run_powershell(
        "Get-CimInstance Win32_ComputerSystem | Select-Object Model | ConvertTo-Json"
    )
    if isinstance(data, dict):
        return data.get("Model", "Unknown")
    return "Unknown"


def _get_motherboard() -> str:
    """获取主板信息"""
    data = _run_powershell(
        "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json"
    )
    if isinstance(data, dict):
        manufacturer = data.get("Manufacturer", "")
        product = data.get("Product", "")
        if manufacturer and product:
            return f"{manufacturer} {product}"
        return manufacturer or product or "Unknown"
    return "Unknown"


def _get_cpu() -> str:
    """获取 CPU 型号"""
    data = _run_powershell(
        "Get-CimInstance Win32_Processor | Select-Object Name | ConvertTo-Json"
    )
    if isinstance(data, dict):
        return data.get("Name", "Unknown")
    # 多个 CPU 的情况
    if isinstance(data, list) and data:
        return data[0].get("Name", "Unknown")
    return "Unknown"


def _get_gpus() -> list[str]:
    """获取显卡型号列表"""
    data = _run_powershell(
        "Get-CimInstance Win32_VideoController | Select-Object Name | ConvertTo-Json"
    )
    if isinstance(data, dict):
        name = data.get("Name", "")
        return [name] if name else []
    if isinstance(data, list):
        return [item.get("Name", "") for item in data if item.get("Name")]
    return []


def get_system_info(device_name_override: str = "") -> SystemInfo:
    """
    获取系统硬件信息

    Args:
        device_name_override: 可选的设备名称覆盖，如果提供则替代系统主机名

    Returns:
        SystemInfo: 包含主机名、电脑型号、主板、CPU、显卡信息的字典
    """
    hostname = device_name_override if device_name_override else socket.gethostname()

    return SystemInfo(
        hostname=hostname,
        computer_model=_get_computer_model(),
        motherboard=_get_motherboard(),
        cpu=_get_cpu(),
        gpus=_get_gpus(),
    )
