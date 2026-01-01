"""
pytest 全局配置和 fixtures

提供整个测试套件共享的配置和 fixtures
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    提供事件循环 fixture
    
    作用域为 session，整个测试会话共享一个事件循环
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config() -> dict:
    """
    提供模拟配置 fixture
    
    Returns:
        包含基础配置的字典
    """
    return {
        "database": {
            "url": "sqlite:///:memory:",
            "echo": False,
            "pool_size": 5,
        },
        "logger": {
            "level": "DEBUG",
            "format": "json",
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "timeout": 30.0,
        },
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    自动重置单例实例
    
    在每个测试后清理单例状态，确保测试隔离
    """
    yield
    # 测试后清理单例实例
    # 可以在这里重置各种单例管理器
