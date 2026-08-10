"""Windows 前台应用显示名查询。"""

from __future__ import annotations

import ctypes
import ntpath
import struct
from ctypes import wintypes

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_MAX_IMAGE_PATH_LENGTH = 32768
_MAX_APPLICATION_NAME_LENGTH = 256
_VERSION_NODE_HEADER_SIZE = 6


class _LanguageAndCodePage(ctypes.Structure):
    _fields_ = [
        ("language", wintypes.WORD),
        ("code_page", wintypes.WORD),
    ]


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_version = ctypes.WinDLL("version", use_last_error=True)

_GetForegroundWindow = _user32.GetForegroundWindow
_GetForegroundWindow.argtypes = []
_GetForegroundWindow.restype = wintypes.HWND

_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD),
]
_GetWindowThreadProcessId.restype = wintypes.DWORD

_OpenProcess = _kernel32.OpenProcess
_OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
_OpenProcess.restype = wintypes.HANDLE

_QueryFullProcessImageNameW = _kernel32.QueryFullProcessImageNameW
_QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
_QueryFullProcessImageNameW.restype = wintypes.BOOL

_CloseHandle = _kernel32.CloseHandle
_CloseHandle.argtypes = [wintypes.HANDLE]
_CloseHandle.restype = wintypes.BOOL

_GetUserDefaultUILanguage = _kernel32.GetUserDefaultUILanguage
_GetUserDefaultUILanguage.argtypes = []
_GetUserDefaultUILanguage.restype = wintypes.WORD

_GetFileVersionInfoSizeW = _version.GetFileVersionInfoSizeW
_GetFileVersionInfoSizeW.argtypes = [
    wintypes.LPCWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
_GetFileVersionInfoSizeW.restype = wintypes.DWORD

_GetFileVersionInfoW = _version.GetFileVersionInfoW
_GetFileVersionInfoW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_void_p,
]
_GetFileVersionInfoW.restype = wintypes.BOOL

_VerQueryValueW = _version.VerQueryValueW
_VerQueryValueW.argtypes = [
    ctypes.c_void_p,
    wintypes.LPCWSTR,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(wintypes.UINT),
]
_VerQueryValueW.restype = wintypes.BOOL


def _normalize_application_name(value: str) -> str | None:
    value = value.strip()
    if (
        not value
        or len(value) > _MAX_APPLICATION_NAME_LENGTH
        or not value.isprintable()
    ):
        return None
    return value


def _get_foreground_executable_path() -> str | None:
    window = _GetForegroundWindow()
    if not window:
        return None

    process_id = wintypes.DWORD()
    if not _GetWindowThreadProcessId(window, ctypes.byref(process_id)):
        return None
    if not process_id.value:
        return None

    process = _OpenProcess(
        _PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        process_id.value,
    )
    if not process:
        return None

    try:
        buffer = ctypes.create_unicode_buffer(_MAX_IMAGE_PATH_LENGTH)
        length = wintypes.DWORD(len(buffer))
        if not _QueryFullProcessImageNameW(
            process,
            0,
            buffer,
            ctypes.byref(length),
        ):
            return None
        return buffer.value or None
    finally:
        _CloseHandle(process)


def _load_version_info(path: str) -> ctypes.Array[ctypes.c_char] | None:
    ignored_handle = wintypes.DWORD()
    size = _GetFileVersionInfoSizeW(path, ctypes.byref(ignored_handle))
    if not size:
        return None

    block = ctypes.create_string_buffer(size)
    if not _GetFileVersionInfoW(path, 0, size, block):
        return None
    return block


def _query_version_value(
    block: ctypes.Array[ctypes.c_char],
    sub_block: str,
) -> tuple[int, int] | None:
    value_pointer = ctypes.c_void_p()
    length = wintypes.UINT()
    if not _VerQueryValueW(
        block,
        sub_block,
        ctypes.byref(value_pointer),
        ctypes.byref(length),
    ):
        return None
    if value_pointer.value is None or not length.value:
        return None
    return value_pointer.value, length.value


def _align_dword(offset: int) -> int:
    return (offset + 3) & ~3


def _read_version_node(
    data: bytes,
    offset: int,
    parent_end: int,
) -> tuple[int, int, str, int] | None:
    """读取一个受父节点边界约束的 VERSIONINFO 节点头。

    Args:
        data: 完整的版本信息缓冲区。
        offset: 当前节点在缓冲区中的起始偏移。
        parent_end: 父节点结束偏移，不包含该位置。

    Returns:
        ``(节点结束偏移, 值长度, 键名, 值起始偏移)``；结构无效时返回
        ``None``。
    """
    if offset < 0 or offset % 4 or parent_end > len(data):
        return None
    if offset + _VERSION_NODE_HEADER_SIZE > parent_end:
        return None

    length, value_length, _value_type = struct.unpack_from("<HHH", data, offset)
    node_end = offset + length
    if length < _VERSION_NODE_HEADER_SIZE or node_end > parent_end:
        return None

    key_start = offset + _VERSION_NODE_HEADER_SIZE
    key_end = key_start
    while key_end + 2 <= node_end:
        if data[key_end : key_end + 2] == b"\0\0":
            break
        key_end += 2
    else:
        return None

    try:
        key = data[key_start:key_end].decode("utf-16-le", errors="strict")
    except UnicodeDecodeError:
        return None

    value_offset = _align_dword(key_end + 2)
    if value_offset > node_end:
        return None
    return node_end, value_length, key, value_offset


def _read_string_table_translations(
    block: ctypes.Array[ctypes.c_char],
) -> list[tuple[int, int]]:
    """从 VERSIONINFO 容器中枚举实际存在的 StringTable 键。

    ``VerQueryValueW`` 不提供 StringTable 枚举能力，因此这里只解析容器层级，
    并严格限制在各节点声明的长度内；最终字符串仍由 Windows API 读取。

    Args:
        block: ``GetFileVersionInfoW`` 填充的版本信息缓冲区。

    Returns:
        按资源顺序去重后的 ``(语言, 代码页)`` 列表；缓冲区无效时返回空列表。
    """
    data = bytes(block)
    root = _read_version_node(data, 0, len(data))
    if root is None:
        return []

    root_end, root_value_length, root_key, root_value_offset = root
    if root_key != "VS_VERSION_INFO":
        return []

    child_offset = _align_dword(root_value_offset + root_value_length)
    if child_offset > root_end:
        return []

    translations: list[tuple[int, int]] = []
    while child_offset + _VERSION_NODE_HEADER_SIZE <= root_end:
        child = _read_version_node(data, child_offset, root_end)
        if child is None:
            return []

        child_end, child_value_length, child_key, child_value_offset = child
        if child_key == "StringFileInfo":
            if child_value_length:
                return []

            table_offset = _align_dword(child_value_offset)
            while table_offset + _VERSION_NODE_HEADER_SIZE <= child_end:
                table = _read_version_node(data, table_offset, child_end)
                if table is None:
                    return []

                table_end, table_value_length, table_key, _table_value_offset = table
                if (
                    not table_value_length
                    and len(table_key) == 8
                    and all(
                        character in "0123456789abcdefABCDEF" for character in table_key
                    )
                ):
                    translations.append(
                        (int(table_key[:4], 16), int(table_key[4:], 16))
                    )
                table_offset = _align_dword(table_end)

        child_offset = _align_dword(child_end)

    return list(dict.fromkeys(translations))


def _read_translations(
    block: ctypes.Array[ctypes.c_char],
) -> list[tuple[int, int]]:
    value = _query_version_value(block, r"\VarFileInfo\Translation")
    entry_size = ctypes.sizeof(_LanguageAndCodePage)
    if value is None or value[1] < entry_size:
        translations = _read_string_table_translations(block)
    else:
        address, length = value
        entry_count = length // entry_size
        entries_type = _LanguageAndCodePage * entry_count
        entries = ctypes.cast(address, ctypes.POINTER(entries_type)).contents
        translations = list(
            dict.fromkeys((entry.language, entry.code_page) for entry in entries)
        )

    try:
        ui_language = _GetUserDefaultUILanguage()
    except OSError:
        ui_language = 0
    if ui_language:
        translations.sort(key=lambda item: item[0] != ui_language)
    return translations


def _read_version_string(
    block: ctypes.Array[ctypes.c_char],
    translation: tuple[int, int],
    field: str,
) -> str | None:
    language, code_page = translation
    sub_block = f"\\StringFileInfo\\{language:04x}{code_page:04x}\\{field}"
    value = _query_version_value(block, sub_block)
    if value is None:
        return None

    address, length = value
    return ctypes.wstring_at(address, length).rstrip("\0")


def _get_version_application_name(path: str) -> str | None:
    block = _load_version_info(path)
    if block is None:
        return None

    translations = _read_translations(block)
    for field in ("FileDescription", "ProductName"):
        for translation in translations:
            value = _read_version_string(block, translation, field)
            normalized = _normalize_application_name(value or "")
            if normalized is not None:
                return normalized
    return None


def get_foreground_application() -> str | None:
    """返回当前前台应用的用户可读名称，无法识别时返回 ``None``。"""
    try:
        path = _get_foreground_executable_path()
    except OSError:
        return None
    if path is None:
        return None

    try:
        version_name = _get_version_application_name(path)
    except (OSError, ValueError):
        version_name = None
    if version_name is not None:
        return version_name

    return _normalize_application_name(ntpath.basename(path))
