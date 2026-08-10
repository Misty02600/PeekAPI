"""Windows 前台应用显示名查询测试。"""

import ctypes
import struct
from unittest.mock import MagicMock, patch

from peekapi import foreground


def _pad_to_dword(data: bytearray):
    data.extend(b"\0" * (-len(data) % 4))


def _version_node(
    key: str,
    *,
    value: bytes = b"",
    value_length: int = 0,
    value_type: int = 1,
    children: tuple[bytes, ...] = (),
) -> bytes:
    data = bytearray(b"\0" * 6)
    data.extend(key.encode("utf-16-le") + b"\0\0")
    _pad_to_dword(data)
    data.extend(value)
    if children:
        _pad_to_dword(data)
        for index, child in enumerate(children):
            data.extend(child)
            if index < len(children) - 1:
                _pad_to_dword(data)
    struct.pack_into("<HHH", data, 0, len(data), value_length, value_type)
    return bytes(data)


def _version_info_with_string_tables(*table_keys: str) -> bytes:
    description = "Translationless App\0"
    string = _version_node(
        "FileDescription",
        value=description.encode("utf-16-le"),
        value_length=len(description),
    )
    tables = tuple(
        _version_node(table_key, children=(string,)) for table_key in table_keys
    )
    string_file_info = _version_node("StringFileInfo", children=tables)
    fixed_file_info = bytes(52)
    return _version_node(
        "VS_VERSION_INFO",
        value=fixed_file_info,
        value_length=len(fixed_file_info),
        value_type=0,
        children=(string_file_info,),
    )


def test_normalize_application_name():
    assert foreground._normalize_application_name(" Visual Studio Code ") == (
        "Visual Studio Code"
    )
    assert foreground._normalize_application_name("微信") == "微信"


def test_normalize_application_name_rejects_unsafe_values():
    assert foreground._normalize_application_name("   ") is None
    assert foreground._normalize_application_name("Code\nEditor") is None
    assert foreground._normalize_application_name("x" * 257) is None


def test_get_foreground_executable_path_closes_process_handle():
    def set_process_id(_window, process_id):
        process_id._obj.value = 42
        return 1

    def set_image_path(_process, _flags, buffer, length):
        value = r"C:\Program Files\Microsoft VS Code\Code.exe"
        buffer.value = value
        length._obj.value = len(value)
        return 1

    with (
        patch.object(foreground, "_GetForegroundWindow", return_value=100),
        patch.object(
            foreground,
            "_GetWindowThreadProcessId",
            side_effect=set_process_id,
        ),
        patch.object(foreground, "_OpenProcess", return_value=200),
        patch.object(
            foreground,
            "_QueryFullProcessImageNameW",
            side_effect=set_image_path,
        ),
        patch.object(foreground, "_CloseHandle") as close_handle,
    ):
        assert foreground._get_foreground_executable_path() == (
            r"C:\Program Files\Microsoft VS Code\Code.exe"
        )

    close_handle.assert_called_once_with(200)


def test_get_foreground_executable_path_handles_missing_window():
    with patch.object(foreground, "_GetForegroundWindow", return_value=0):
        assert foreground._get_foreground_executable_path() is None


def test_get_foreground_executable_path_handles_process_lookup_failure():
    with (
        patch.object(foreground, "_GetForegroundWindow", return_value=100),
        patch.object(foreground, "_GetWindowThreadProcessId", return_value=0),
        patch.object(foreground, "_OpenProcess") as open_process,
    ):
        assert foreground._get_foreground_executable_path() is None

    open_process.assert_not_called()


def test_get_foreground_executable_path_handles_open_process_failure():
    def set_process_id(_window, process_id):
        process_id._obj.value = 42
        return 1

    with (
        patch.object(foreground, "_GetForegroundWindow", return_value=100),
        patch.object(
            foreground,
            "_GetWindowThreadProcessId",
            side_effect=set_process_id,
        ),
        patch.object(foreground, "_OpenProcess", return_value=0),
        patch.object(foreground, "_CloseHandle") as close_handle,
    ):
        assert foreground._get_foreground_executable_path() is None

    close_handle.assert_not_called()


def test_get_foreground_executable_path_closes_handle_when_query_fails():
    def set_process_id(_window, process_id):
        process_id._obj.value = 42
        return 1

    with (
        patch.object(foreground, "_GetForegroundWindow", return_value=100),
        patch.object(
            foreground,
            "_GetWindowThreadProcessId",
            side_effect=set_process_id,
        ),
        patch.object(foreground, "_OpenProcess", return_value=200),
        patch.object(foreground, "_QueryFullProcessImageNameW", return_value=0),
        patch.object(foreground, "_CloseHandle") as close_handle,
    ):
        assert foreground._get_foreground_executable_path() is None

    close_handle.assert_called_once_with(200)


def test_load_version_info_handles_missing_resource():
    with patch.object(foreground, "_GetFileVersionInfoSizeW", return_value=0):
        assert foreground._load_version_info("Code.exe") is None


def test_load_version_info_handles_read_failure():
    with (
        patch.object(foreground, "_GetFileVersionInfoSizeW", return_value=16),
        patch.object(foreground, "_GetFileVersionInfoW", return_value=0),
    ):
        assert foreground._load_version_info("Code.exe") is None


def test_load_version_info_returns_buffer():
    def write_version_info(_path, _handle, _size, block):
        block[0] = b"x"
        return 1

    with (
        patch.object(foreground, "_GetFileVersionInfoSizeW", return_value=16),
        patch.object(
            foreground,
            "_GetFileVersionInfoW",
            side_effect=write_version_info,
        ),
    ):
        block = foreground._load_version_info("Code.exe")

    assert block is not None
    assert block[0] == b"x"


def test_read_translations_prioritizes_user_ui_language():
    translations = (foreground._LanguageAndCodePage * 2)(
        foreground._LanguageAndCodePage(0x0409, 1200),
        foreground._LanguageAndCodePage(0x0804, 1200),
    )
    block = ctypes.create_string_buffer(1)

    with (
        patch.object(
            foreground,
            "_query_version_value",
            return_value=(ctypes.addressof(translations), ctypes.sizeof(translations)),
        ),
        patch.object(
            foreground,
            "_GetUserDefaultUILanguage",
            return_value=0x0804,
        ),
        patch.object(foreground, "_read_string_table_translations") as fallback,
    ):
        assert foreground._read_translations(block) == [
            (0x0804, 1200),
            (0x0409, 1200),
        ]

    fallback.assert_not_called()


def test_read_translations_falls_back_to_actual_string_tables():
    data = _version_info_with_string_tables("040904B0", "080404B0")
    block = ctypes.create_string_buffer(data, len(data))

    with (
        patch.object(foreground, "_query_version_value", return_value=None),
        patch.object(
            foreground,
            "_GetUserDefaultUILanguage",
            return_value=0x0804,
        ),
    ):
        assert foreground._read_translations(block) == [
            (0x0804, 1200),
            (0x0409, 1200),
        ]


def test_read_translations_rejects_truncated_version_info():
    block = ctypes.create_string_buffer(b"\xff\xff\0\0\0\0", 6)

    with patch.object(foreground, "_query_version_value", return_value=None):
        assert foreground._read_translations(block) == []


def test_read_version_string_supports_unicode():
    value = ctypes.create_unicode_buffer("Visual Studio Code")
    block = ctypes.create_string_buffer(1)

    with patch.object(
        foreground,
        "_query_version_value",
        return_value=(ctypes.addressof(value), len(value)),
    ):
        assert (
            foreground._read_version_string(
                block,
                (0x0409, 1200),
                "FileDescription",
            )
            == "Visual Studio Code"
        )


def test_version_application_name_prefers_file_description():
    block = ctypes.create_string_buffer(1)

    def read_string(_block, _translation, field):
        return {
            "FileDescription": "Visual Studio Code",
            "ProductName": "Ignored Product",
        }[field]

    with (
        patch.object(foreground, "_load_version_info", return_value=block),
        patch.object(foreground, "_read_translations", return_value=[(0x0409, 1200)]),
        patch.object(
            foreground,
            "_read_version_string",
            side_effect=read_string,
        ) as read_version_string,
    ):
        assert (
            foreground._get_version_application_name("Code.exe") == "Visual Studio Code"
        )

    read_version_string.assert_called_once_with(
        block,
        (0x0409, 1200),
        "FileDescription",
    )


def test_version_application_name_falls_back_to_product_name():
    block = ctypes.create_string_buffer(1)

    def read_string(_block, _translation, field):
        return None if field == "FileDescription" else "示例应用"

    with (
        patch.object(foreground, "_load_version_info", return_value=block),
        patch.object(foreground, "_read_translations", return_value=[(0x0804, 1200)]),
        patch.object(
            foreground,
            "_read_version_string",
            side_effect=read_string,
        ),
    ):
        assert foreground._get_version_application_name("app.exe") == "示例应用"


def test_version_application_name_prefers_description_across_translations():
    block = ctypes.create_string_buffer(1)
    translations = [(0x0409, 1200), (0x0804, 1200)]

    def read_string(_block, translation, field):
        values = {
            ((0x0409, 1200), "ProductName"): "English Product",
            ((0x0804, 1200), "FileDescription"): "中文描述",
        }
        return values.get((translation, field))

    with (
        patch.object(foreground, "_load_version_info", return_value=block),
        patch.object(foreground, "_read_translations", return_value=translations),
        patch.object(
            foreground,
            "_read_version_string",
            side_effect=read_string,
        ),
    ):
        assert foreground._get_version_application_name("app.exe") == "中文描述"


def test_version_application_name_reads_resource_without_translation_table():
    data = _version_info_with_string_tables("040904B0")
    block = ctypes.create_string_buffer(data, len(data))

    with (
        patch.object(foreground, "_load_version_info", return_value=block),
        patch.object(
            foreground,
            "_GetUserDefaultUILanguage",
            return_value=0x0409,
        ),
    ):
        assert (
            foreground._get_version_application_name("app.exe") == "Translationless App"
        )


def test_get_foreground_application_falls_back_to_basename():
    with (
        patch.object(
            foreground,
            "_get_foreground_executable_path",
            return_value=r"C:\Tools\app.exe",
        ),
        patch.object(foreground, "_get_version_application_name", return_value=None),
    ):
        assert foreground.get_foreground_application() == "app.exe"


def test_get_foreground_application_handles_windows_error():
    with patch.object(
        foreground,
        "_get_foreground_executable_path",
        side_effect=OSError,
    ):
        assert foreground.get_foreground_application() is None


def test_query_version_value_rejects_missing_pointer():
    block = ctypes.create_string_buffer(1)
    api = MagicMock(return_value=1)

    with patch.object(foreground, "_VerQueryValueW", api):
        assert foreground._query_version_value(block, "test") is None


def test_query_version_value_returns_pointer_and_length():
    block = ctypes.create_string_buffer(1)
    value = ctypes.create_unicode_buffer("Code")

    def query_value(_block, _sub_block, pointer, length):
        pointer._obj.value = ctypes.addressof(value)
        length._obj.value = len(value)
        return 1

    with patch.object(
        foreground,
        "_VerQueryValueW",
        side_effect=query_value,
    ):
        assert foreground._query_version_value(block, "test") == (
            ctypes.addressof(value),
            len(value),
        )
