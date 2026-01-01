"""
kernel 层测试配置和 fixtures
"""

import pytest
from typing import AsyncGenerator


@pytest.fixture
async def mock_db_engine():
    """提供模拟数据库引擎"""
    # 这里创建内存数据库引擎
    # engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # yield engine
    # await engine.dispose()
    pass


@pytest.fixture
def mock_llm_client():
    """提供模拟 LLM 客户端"""
    pass


@pytest.fixture
async def mock_vector_db():
    """提供模拟向量数据库"""
    pass
