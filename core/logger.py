"""
logger.py  —  统一日志配置模块
提供全局日志实例，避免各模块重复配置
"""

import logging
import sys
from pathlib import Path


def setup_logging(level: int = logging.INFO, log_file: str | None = None) -> None:
    """
    配置全局日志格式
    
    Args:
        level: 日志级别，默认 INFO
        log_file: 可选的日志文件路径
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志实例"""
    return logging.getLogger(name)
