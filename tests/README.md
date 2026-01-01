# MoFox 测试套件

本目录包含 MoFox 项目的所有测试文件，严格遵循 100% 覆盖率要求。

## 目录结构

测试目录结构与源码目录完全对应：

```
tests/
├── README.md                    # 本文件
├── conftest.py                  # pytest 全局配置和 fixtures
├── kernel/                      # kernel 层测试
│   ├── conftest.py
│   ├── concurrency/
│   │   ├── __init__.py
│   │   ├── test_watchdog.py
│   │   └── test_task_manager.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── test_config_base.py
│   │   └── test_config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── test_engine.py
│   │   │   ├── test_session.py
│   │   │   └── ...
│   │   ├── api/
│   │   │   ├── test_crud.py
│   │   │   └── test_query.py
│   │   └── optimization/
│   │       └── test_cache_manager.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_llm_request.py
│   │   ├── model_client/
│   │   │   ├── test_base_client.py
│   │   │   ├── test_openai_client.py
│   │   │   └── ...
│   │   └── payload/
│   │       ├── test_message.py
│   │       └── ...
│   ├── logger/
│   ├── storage/
│   └── vector_db/
└── core/                        # core 层测试
    ├── conftest.py
    ├── components/
    │   ├── base/
    │   │   ├── test_action.py
    │   │   ├── test_adapter.py
    │   │   └── ...
    │   └── managers/
    │       ├── test_action_manager.py
    │       └── ...
    ├── prompt/
    ├── perception/
    ├── transport/
    └── models/
```

## 测试规范

### 命名规范
- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试函数：`test_<function_name>_<scenario>`

### 测试类型

#### 1. 单元测试（Unit Tests）
- 测试单个函数或方法
- 使用 mock 隔离外部依赖
- 快速执行，无 I/O 操作

```python
# 示例：tests/kernel/concurrency/test_watchdog.py
import pytest
from mofox_src.kernel.concurrency.watchdog import Watchdog, TaskStatus

class TestWatchdog:
    def test_get_instance_returns_singleton(self):
        """测试 Watchdog 返回单例实例"""
        watchdog1 = Watchdog.get_instance()
        watchdog2 = Watchdog.get_instance()
        assert watchdog1 is watchdog2
    
    @pytest.mark.asyncio
    async def test_register_task_success(self):
        """测试成功注册任务"""
        watchdog = Watchdog.get_instance()
        task = asyncio.create_task(asyncio.sleep(1))
        task_id = watchdog.register_task(task, name="test_task")
        
        assert task_id is not None
        task_info = watchdog.get_task_info(task_id)
        assert task_info.name == "test_task"
```

#### 2. 集成测试（Integration Tests）
- 测试多个模块协作
- 可使用真实依赖或测试数据库
- 标记为 `@pytest.mark.integration`

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_watchdog_with_task_manager():
    """测试 Watchdog 与 TaskManager 集成"""
    # 集成测试代码
    pass
```

#### 3. 异步测试
- 使用 `@pytest.mark.asyncio` 装饰器
- 测试异步函数和协程

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

## Fixtures

### 全局 Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """提供事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config():
    """提供模拟配置"""
    return {
        "database": {"url": "sqlite:///:memory:"},
        "logger": {"level": "DEBUG"}
    }
```

### 模块级 Fixtures

每个测试子目录可以有自己的 `conftest.py` 提供模块特定的 fixtures。

## 运行测试

### 运行所有测试
```bash
pytest tests/
```

### 运行特定模块测试
```bash
# 测试 kernel 层
pytest tests/kernel/

# 测试特定文件
pytest tests/kernel/concurrency/test_watchdog.py

# 测试特定函数
pytest tests/kernel/concurrency/test_watchdog.py::TestWatchdog::test_register_task_success
```

### 测试覆盖率
```bash
# 生成覆盖率报告
pytest tests/ --cov=mofox_src --cov-report=html --cov-report=term-missing

# 只看 kernel 层覆盖率
pytest tests/kernel/ --cov=mofox_src.kernel --cov-report=term-missing

# 查看详细报告
# 打开 htmlcov/index.html
```

### 并行测试
```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行运行测试
pytest tests/ -n auto
```

### 测试筛选

```bash
# 只运行单元测试（默认）
pytest tests/ -m "not integration"

# 只运行集成测试
pytest tests/ -m integration

# 运行慢速测试
pytest tests/ -m slow

# 跳过慢速测试
pytest tests/ -m "not slow"
```

## 覆盖率要求

### 强制要求
- **kernel 层：100% 覆盖率**
- **core 层：100% 覆盖率**
- app 层：建议 ≥ 80%

### 覆盖率检查
```bash
# 检查是否达到 100%
pytest tests/kernel/ --cov=mofox_src.kernel --cov-fail-under=100
pytest tests/core/ --cov=mofox_src.core --cov-fail-under=100
```

### 覆盖率报告解读
```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
mofox_src/kernel/watchdog.py       145      0   100%
mofox_src/kernel/task_manager.py    89      5    94%   23-27
```

- **Stmts**：语句总数
- **Miss**：未覆盖语句数
- **Cover**：覆盖率百分比
- **Missing**：未覆盖的行号

## Mock 与 Patch

### 使用 pytest-mock

```python
def test_with_mock(mocker):
    """使用 mocker fixture"""
    mock_func = mocker.patch('module.function')
    mock_func.return_value = "mocked"
    
    result = call_function_that_uses_module_function()
    assert result == "expected"
    mock_func.assert_called_once()
```

### Mock 异步函数

```python
@pytest.mark.asyncio
async def test_async_mock(mocker):
    """Mock 异步函数"""
    mock_async = mocker.patch('module.async_function')
    mock_async.return_value = asyncio.Future()
    mock_async.return_value.set_result("mocked")
    
    result = await call_async_function()
    assert result == "expected"
```

## 测试数据

### Fixtures 提供测试数据

```python
@pytest.fixture
def sample_task_info():
    """提供示例任务信息"""
    return TaskInfo(
        task_id="test_001",
        name="TestTask",
        task=asyncio.create_task(asyncio.sleep(0)),
        timeout=30.0
    )
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input, expected):
    """参数化测试"""
    assert multiply_by_two(input) == expected
```

## 最佳实践

### 1. AAA 模式
```python
def test_example():
    # Arrange - 准备
    watchdog = Watchdog.get_instance()
    
    # Act - 执行
    result = watchdog.get_stats()
    
    # Assert - 断言
    assert result['total_registered'] >= 0
```

### 2. 清理资源
```python
@pytest.fixture
async def watchdog():
    """提供 Watchdog 实例并自动清理"""
    wd = Watchdog.get_instance()
    await wd.start()
    yield wd
    await wd.stop()
```

### 3. 测试隔离
- 每个测试应独立运行
- 不依赖其他测试的执行顺序
- 清理测试产生的副作用

### 4. 有意义的断言
```python
# ❌ 不好
assert result == True

# ✅ 好
assert result is True
assert len(tasks) == expected_count
assert task_info.status == TaskStatus.RUNNING
```

### 5. 测试异常
```python
def test_exception_raised():
    """测试异常抛出"""
    with pytest.raises(ValueError, match="Invalid task ID"):
        watchdog.get_task_info("invalid_id")
```

## 持续集成

### GitHub Actions 配置示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=mofox_src --cov-fail-under=100
```

## 常见问题

### Q: 如何测试单例类？
A: 在 fixture 中重置单例实例，或使用 `mocker.patch.object`。

### Q: 异步测试超时怎么办？
A: 使用 `@pytest.mark.timeout(10)` 设置超时时间。

### Q: 如何 mock 文件操作？
A: 使用 `mocker.patch('builtins.open')` 或 `tmp_path` fixture。

### Q: 测试数据库操作？
A: 使用内存数据库（SQLite `:memory:`）或 Docker 容器。

## 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [pytest-mock](https://github.com/pytest-dev/pytest-mock)
- [pytest-cov](https://github.com/pytest-dev/pytest-cov)
