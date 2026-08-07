"""Windows 电源事件处理模块测试。"""

from unittest.mock import MagicMock

from peekapi import power_events


def test_suspend_requests_stop_without_waiting(monkeypatch):
    recorder = MagicMock()
    monkeypatch.setattr(power_events, "_recorder_ref", recorder)
    monkeypatch.setattr(power_events, "_suspended", False)

    result = power_events._on_power_event(
        None,
        power_events.PBT_APMSUSPEND,
        None,
    )

    assert result == 0
    assert power_events._suspended is True
    recorder.stop_recording.assert_called_once_with(wait=False)


def test_resume_clears_suspended_only_after_start_is_accepted(monkeypatch):
    recorder = MagicMock()
    monkeypatch.setattr(power_events, "_recorder_ref", recorder)
    monkeypatch.setattr(power_events, "_suspended", True)

    result = power_events._on_power_event(
        None,
        power_events.PBT_APMRESUMEAUTOMATIC,
        None,
    )

    assert result == 0
    assert power_events._suspended is False
    recorder.start_recording.assert_called_once_with()


def test_resume_start_failure_keeps_suspended_for_retry(monkeypatch):
    recorder = MagicMock()
    recorder.start_recording.side_effect = RuntimeError("start failed")
    monkeypatch.setattr(power_events, "_recorder_ref", recorder)
    monkeypatch.setattr(power_events, "_suspended", True)

    result = power_events._on_power_event(
        None,
        power_events.PBT_APMRESUMEAUTOMATIC,
        None,
    )

    assert result == 0
    assert power_events._suspended is True
    recorder.start_recording.assert_called_once_with()


def test_duplicate_suspend_and_resume_notifications_are_ignored(monkeypatch):
    recorder = MagicMock()
    monkeypatch.setattr(power_events, "_recorder_ref", recorder)
    monkeypatch.setattr(power_events, "_suspended", False)

    power_events._on_power_event(None, power_events.PBT_APMSUSPEND, None)
    power_events._on_power_event(None, power_events.PBT_APMSUSPEND, None)
    power_events._on_power_event(None, power_events.PBT_APMRESUMEAUTOMATIC, None)
    power_events._on_power_event(None, power_events.PBT_APMRESUMESUSPEND, None)

    recorder.stop_recording.assert_called_once_with(wait=False)
    recorder.start_recording.assert_called_once_with()
    assert power_events._suspended is False
