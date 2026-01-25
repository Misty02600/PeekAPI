"""日志配置模块"""

import sys

from loguru import logger

from .constants import LOG_DIR


def setup_logging(console: bool = False) -> None:
    """配置日志系统

    Args:
        console: 是否同时输出到控制台
    """
    # 移除默认 handler
    logger.remove()

    # 确保日志目录存在
    LOG_DIR.mkdir(exist_ok=True)

    # 文件日志（按日期轮转）
    logger.add(
        LOG_DIR / "peekapi_{time:YYYYMMDD}.log",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留 7 天
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {name}: {message}",
        level="INFO",
    )

    # 控制台输出（可选）
    if console:
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: {message}",
            level="INFO",
            colorize=True,
        )

    logger.info("PeekAPI 日志系统初始化完成")


__all__ = ["logger", "setup_logging"]
