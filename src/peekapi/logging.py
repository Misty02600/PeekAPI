"""日志配置模块"""

import sys

from loguru import logger

from .constants import LOG_DIR


def setup_logging() -> None:
    """配置日志系统，日志输出到控制台和文件"""
    # 移除默认 handler（重新配置格式）
    logger.remove()

    # 确保日志目录存在
    LOG_DIR.mkdir(exist_ok=True)

    # 控制台日志
    logger.add(
        sink=sys.stderr,
        format="{time:HH:mm:ss} [{level}] {message}",
        level="INFO",
        colorize=True,
    )

    # 文件日志（按日期轮转）
    logger.add(
        LOG_DIR / "peekapi_{time:YYYYMMDD}.log",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留 7 天
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {name}: {message}",
        level="INFO",
    )


__all__ = ["logger", "setup_logging"]
