"""
core 层测试配置和 fixtures
"""

import pytest


@pytest.fixture
def mock_component_registry():
    """提供模拟组件注册表"""
    pass


@pytest.fixture
def mock_state_manager():
    """提供模拟状态管理器"""
    pass


@pytest.fixture
def mock_event_manager():
    """提供模拟事件管理器"""
    pass


@pytest.fixture
def mock_adapter():
    """提供模拟适配器"""
    pass
