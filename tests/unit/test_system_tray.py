"""系统托盘自启菜单测试。"""

from unittest.mock import MagicMock

from peekapi import system_tray


def test_toggle_autostart_enables_and_refreshes_menu(monkeypatch):
    icon = MagicMock()
    monkeypatch.setattr(system_tray, "is_autostart_enabled", lambda: False)
    enable = MagicMock(return_value=True)
    monkeypatch.setattr(system_tray, "enable_autostart", enable)

    system_tray.toggle_autostart(icon, None)

    enable.assert_called_once_with()
    icon.update_menu.assert_called_once_with()


def test_toggle_autostart_disables_and_refreshes_menu(monkeypatch):
    icon = MagicMock()
    monkeypatch.setattr(system_tray, "is_autostart_enabled", lambda: True)
    disable = MagicMock(return_value=True)
    monkeypatch.setattr(system_tray, "disable_autostart", disable)

    system_tray.toggle_autostart(icon, None)

    disable.assert_called_once_with()
    icon.update_menu.assert_called_once_with()


def test_toggle_autostart_failure_is_isolated(monkeypatch):
    icon = MagicMock()

    def fail_query():
        raise system_tray.AutostartError("query failed")

    monkeypatch.setattr(system_tray, "is_autostart_enabled", fail_query)
    warning = MagicMock()
    monkeypatch.setattr(system_tray.logger, "warning", warning)

    system_tray.toggle_autostart(icon, None)

    warning.assert_called_once()
    icon.update_menu.assert_called_once_with()


def test_checked_query_failure_returns_false(monkeypatch):
    def fail_query():
        raise system_tray.AutostartError("query failed")

    monkeypatch.setattr(system_tray, "is_autostart_enabled", fail_query)
    monkeypatch.setattr(system_tray.logger, "warning", MagicMock())

    assert system_tray._is_autostart_checked(None) is False
