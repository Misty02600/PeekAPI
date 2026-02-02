"""集成测试共享 fixtures"""

import pytest


def pytest_configure(config):
    """注册自定义 markers"""
    config.addinivalue_line("markers", "integration: 集成测试，需要真实硬件环境")


@pytest.fixture
def skip_in_ci():
    """CI 环境跳过"""
    import os

    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        pytest.skip("CI 环境跳过集成测试")
