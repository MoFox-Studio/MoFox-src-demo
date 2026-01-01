# MoFox 贡献指南

欢迎为 MoFox 项目做出贡献！本指南将帮助你了解如何为项目贡献代码、文档和测试。

## 📋 目录

- [贡献流程](#贡献流程)
- [分层架构与审查标准](#分层架构与审查标准)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [文档要求](#文档要求)
- [提交规范](#提交规范)
- [审查流程](#审查流程)
- [质量检查清单](#质量检查清单)

---

## 贡献流程

### 1. 准备工作

```bash
# Fork 并克隆仓库
git clone https://github.com/your-username/mofox.git
cd mofox

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 创建功能分支

```bash
# 从主分支创建新分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/bug-description
```

### 3. 开发与测试

```bash
# 运行测试
pytest tests/ -v

# 检查代码覆盖率
pytest --cov=mofox_src --cov-report=html

# 代码格式化
black mofox-src/ tests/

# 代码风格检查
flake8 mofox-src/ tests/

# 类型检查
mypy mofox-src/
```

### 4. 提交代码

```bash
# 添加修改
git add .

# 提交（遵循提交规范）
git commit -m "feat(kernel/concurrency): add timeout callback feature"

# 推送到远程
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

- 在 GitHub 上创建 PR
- 填写 PR 模板
- 等待代码审查
- 根据反馈修改代码

---

## 分层架构与审查标准

MoFox 采用严格的三层架构，不同层级有不同的质量要求和审查标准。

### 架构层级

```
┌─────────────────────────────────────┐
│         App Layer (应用层)           │  ← 灵活，快速迭代
│   插件、装配、高级 API                │
├─────────────────────────────────────┤
│         Core Layer (核心层)          │  ← 严格审查 ⚠️
│   记忆、对话、行为、组件管理          │
├─────────────────────────────────────┤
│        Kernel Layer (内核层)         │  ← 最严格审查 ⚠️⚠️
│   数据库、LLM、日志、并发、配置       │
└─────────────────────────────────────┘
```

### 🔴 Kernel 层：最严格审查标准

**定位**: 提供与业务无关的基础技术能力

**质量要求**:
- ✅ **100% 测试覆盖率**（强制）
- ✅ **100% 文档覆盖率**（强制）
- ✅ **至少 2 名核心维护者审查**（强制）
- ✅ **性能基准测试**（推荐）
- ✅ **向后兼容性保证**（强制）

**审查重点**:
1. **API 稳定性**: 任何公共 API 变更都需要详细的兼容性说明
2. **性能影响**: 需提供性能测试结果
3. **错误处理**: 完善的异常处理和错误恢复机制
4. **资源管理**: 内存泄漏检测、连接池管理等
5. **线程/并发安全**: 明确的并发模型和安全保证
6. **依赖管理**: 最小化外部依赖，避免版本冲突

**审查流程**:
```
提交 PR → 自动化测试 → 代码覆盖率检查 → 架构师初审 
    → 核心维护者审查 → 性能测试 → 文档审查 → 合并
```

**示例模块**: 
- `kernel/db/` - 数据库抽象
- `kernel/llm/` - LLM 请求系统
- `kernel/concurrency/` - 并发管理
- `kernel/logger/` - 日志系统

### 🟡 Core 层：严格审查标准

**定位**: 使用 Kernel 能力实现核心业务逻辑

**质量要求**:
- ✅ **100% 测试覆盖率**（强制）
- ✅ **100% 文档覆盖率**（强制）
- ✅ **至少 1 名核心维护者审查**（强制）
- ✅ **集成测试**（强制）
- ⚠️ **向后兼容性**（尽量保证）

**审查重点**:
1. **业务逻辑正确性**: 核心功能的正确实现
2. **模块间依赖**: 合理的依赖关系，避免循环依赖
3. **扩展性设计**: 便于未来扩展和插件化
4. **状态管理**: 正确的状态同步和一致性保证
5. **Kernel 层使用**: 正确使用 Kernel 提供的能力

**审查流程**:
```
提交 PR → 自动化测试 → 代码覆盖率检查 → 核心维护者审查 
    → 集成测试 → 文档审查 → 合并
```

**示例模块**:
- `core/components/` - 组件系统
- `core/perception/` - 感知学习
- `core/prompt/` - Prompt 管理
- `core/transport/` - 通讯传输

### 🟢 App 层：常规审查标准

**定位**: 组装 Kernel 和 Core 成可运行系统

**质量要求**:
- ⚠️ **测试覆盖率 > 80%**（推荐）
- ⚠️ **文档覆盖关键功能**（推荐）
- ✅ **至少 1 名维护者审查**（推荐）
- ✅ **端到端测试**（推荐）

**审查重点**:
1. **用户体验**: 易用性和功能完整性
2. **插件兼容性**: 插件接口设计和版本兼容
3. **配置合理性**: 配置项的设计和默认值
4. **错误提示**: 友好的错误信息和调试信息

---

## 代码规范

### Python 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范，使用以下工具确保一致性：

```bash
# 代码格式化（自动修复）
black mofox-src/ tests/ --line-length 88

# 代码风格检查
flake8 mofox-src/ tests/ --max-line-length 88 --extend-ignore E203,W503

# 类型检查
mypy mofox-src/ --strict
```

### 命名规范

```python
# 模块名：小写下划线
# 文件名: task_manager.py

# 类名：大驼峰
class TaskManager:
    pass

# 函数/方法名：小写下划线
def get_task_info():
    pass

# 常量：大写下划线
MAX_RETRY_COUNT = 3

# 私有成员：单下划线前缀
def _internal_method():
    pass

# 强私有成员：双下划线前缀
def __private_method():
    pass
```

### 类型注解

**Kernel 和 Core 层必须使用类型注解**：

```python
from typing import Optional, List, Dict, Any

def process_task(
    task_id: str,
    timeout: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    处理任务
    
    Args:
        task_id: 任务ID
        timeout: 超时时间（秒）
        metadata: 任务元数据
    
    Returns:
        处理是否成功
    """
    pass
```

### 文档字符串

使用 Google 风格的 docstring：

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    函数的简短描述（一行）
    
    更详细的描述，可以多行。解释函数的作用、
    使用场景、注意事项等。
    
    Args:
        param1: 第一个参数的描述
        param2: 第二个参数的描述
        
    Returns:
        返回值的描述，包括数据结构
        
    Raises:
        ValueError: 参数无效时抛出
        ConnectionError: 连接失败时抛出
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### 错误处理

```python
# ❌ 不好的做法
def bad_function():
    try:
        result = risky_operation()
    except:  # 捕获所有异常
        pass  # 静默失败

# ✅ 好的做法
def good_function():
    try:
        result = risky_operation()
    except SpecificError as e:
        logger.error(f"Operation failed: {e}")
        raise  # 或者进行适当的错误处理
    except AnotherError as e:
        # 转换为更合适的异常
        raise CustomError(f"Failed to process: {e}") from e
```

---

## 测试要求

### Kernel 和 Core 层：100% 覆盖率

每个模块文件都必须有对应的测试文件：

```
mofox-src/kernel/concurrency/watchdog.py
→ tests/kernel/concurrency/test_watchdog.py
```

### 测试文件结构

```python
"""
watchdog.py 的测试文件

测试覆盖：
- TaskStatus 枚举
- TaskInfo 数据类
- Watchdog 单例模式
- 任务注册与追踪
- 超时检测
- 回调触发
- 统计功能
"""

import pytest
import asyncio
from mofox.kernel.concurrency.watchdog import (
    Watchdog, TaskStatus, TaskInfo, get_watchdog, watch_task
)


class TestTaskStatus:
    """测试 TaskStatus 枚举"""
    
    def test_all_statuses(self):
        """测试所有状态值"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        # ...


class TestTaskInfo:
    """测试 TaskInfo 数据类"""
    
    def test_duration_calculation(self):
        """测试运行时长计算"""
        # ...
    
    def test_is_timeout(self):
        """测试超时判断"""
        # ...


class TestWatchdog:
    """测试 Watchdog 主类"""
    
    @pytest.fixture
    async def watchdog(self):
        """提供干净的 watchdog 实例"""
        wd = Watchdog.get_instance()
        await wd.start()
        yield wd
        await wd.stop()
        wd._tasks.clear()
    
    async def test_singleton(self):
        """测试单例模式"""
        wd1 = Watchdog.get_instance()
        wd2 = get_watchdog()
        assert wd1 is wd2
    
    async def test_register_task(self, watchdog):
        """测试任务注册"""
        task = asyncio.create_task(asyncio.sleep(1))
        task_id = watchdog.register_task(task, name="test")
        
        assert task_id in watchdog._tasks
        assert watchdog._tasks[task_id].name == "test"
    
    async def test_timeout_detection(self, watchdog):
        """测试超时检测"""
        timeout_called = False
        
        def on_timeout(tid, info):
            nonlocal timeout_called
            timeout_called = True
        
        watchdog.add_timeout_callback(on_timeout)
        
        task, task_id = await watch_task(
            asyncio.sleep(10),
            timeout=0.5
        )
        
        await asyncio.sleep(1)
        assert timeout_called
        assert task.cancelled()
```

### 测试类型

1. **单元测试**: 测试单个函数/方法
2. **集成测试**: 测试模块间协作
3. **异步测试**: 使用 `pytest-asyncio`
4. **Mock 测试**: 使用 `pytest-mock` 隔离依赖
5. **参数化测试**: 使用 `@pytest.mark.parametrize`

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/kernel/concurrency/test_watchdog.py -v

# 检查覆盖率
pytest --cov=mofox_src --cov-report=html --cov-report=term

# 只运行失败的测试
pytest --lf

# 并行运行测试
pytest -n auto
```

---

## 文档要求

### Kernel 和 Core 层：100% 文档覆盖率

每个模块文件都必须有对应的 Markdown 文档：

```
mofox-src/kernel/concurrency/watchdog.py
→ docs/kernel/concurrency/watchdog.md
```

### 文档结构模板

```markdown
# 模块名称

## 概述

简要描述模块的功能和作用。

## 主要功能

列出主要功能点：
1. 功能一
2. 功能二
3. 功能三

## 核心组件

### ClassName 类

类的详细说明。

**属性**:
- `attr1` (type): 属性说明
- `attr2` (type): 属性说明

**方法**:

#### `method_name(param1, param2) -> ReturnType`

方法描述。

参数:
- `param1` (type): 参数说明
- `param2` (type): 参数说明

返回:
- `ReturnType`: 返回值说明

示例:
    代码示例

## 使用示例

### 基本使用

\```python
# 代码示例
\```

### 高级用法

\```python
# 更复杂的示例
\```

## 工作原理

解释内部实现机制。

## 注意事项

列出使用限制和注意事项。

## 最佳实践

提供使用建议。

## 相关模块

链接到相关文档。

## 版本历史

记录重要变更。
```

### 文档检查清单

- [ ] 有清晰的概述
- [ ] 列出所有公共 API
- [ ] 包含实际可运行的代码示例
- [ ] 说明参数和返回值类型
- [ ] 标注异常情况
- [ ] 提供注意事项和最佳实践
- [ ] 链接到相关模块文档

---

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（不是新功能也不是修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

### Scope 范围

指明修改的模块，例如：
- `kernel/db`
- `kernel/llm`
- `core/components`
- `core/prompt`

### 示例

```bash
# 新功能
git commit -m "feat(kernel/concurrency): add timeout callback feature"

# Bug 修复
git commit -m "fix(kernel/db): fix connection pool leak"

# 文档更新
git commit -m "docs(kernel/concurrency): add watchdog usage examples"

# 重构
git commit -m "refactor(core/components): simplify manager initialization"

# 性能优化
git commit -m "perf(kernel/llm): optimize request batching"
```

### Breaking Changes

如果有破坏性变更，在 footer 中说明：

```bash
git commit -m "feat(kernel/db): change session API

BREAKING CHANGE: Session.query() now returns AsyncIterator instead of List.
Migration guide: ...
"
```

---

## 审查流程

### PR 提交清单

创建 PR 前，请确认：

- [ ] 代码通过所有测试
- [ ] 测试覆盖率达标（Kernel/Core: 100%, App: >80%）
- [ ] 代码格式化完成（black）
- [ ] 代码风格检查通过（flake8）
- [ ] 类型检查通过（mypy，Kernel/Core 层）
- [ ] 文档已更新
- [ ] CHANGELOG 已更新（如适用）
- [ ] 提交信息符合规范

### Kernel 层 PR 审查

**自动检查**:
```bash
# CI 自动运行
- pytest --cov=mofox_src/kernel --cov-report=term --cov-fail-under=100
- black --check mofox-src/kernel
- flake8 mofox-src/kernel
- mypy mofox-src/kernel --strict
```

**人工审查重点**:
1. **架构设计**: API 设计是否合理、是否符合 SOLID 原则
2. **性能影响**: 是否有性能测试结果、对现有功能的影响
3. **错误处理**: 异常处理是否完善、错误信息是否清晰
4. **资源管理**: 是否正确管理资源（文件、连接、内存等）
5. **并发安全**: 是否考虑并发场景、是否有竞态条件
6. **向后兼容**: API 变更是否兼容、是否需要迁移指南
7. **文档完整性**: 文档是否清晰、示例是否可运行
8. **测试质量**: 测试是否覆盖边界情况、是否有集成测试

**审查流程**:
```
PR 创建 → 自动化测试（5-10分钟）
    ↓
CI 通过 → 架构师初审（1-2天）
    ↓
初审通过 → 核心维护者审查（2-3天）
    ↓
代码 LGTM → 性能测试（如需要）
    ↓
全部通过 → 合并到主分支
```

### Core 层 PR 审查

**自动检查**:
```bash
- pytest --cov=mofox_src/core --cov-report=term --cov-fail-under=100
- black --check mofox-src/core
- flake8 mofox-src/core
- mypy mofox-src/core --strict
```

**人工审查重点**:
1. **业务逻辑**: 功能实现是否正确、是否符合需求
2. **模块依赖**: 依赖关系是否合理、是否有循环依赖
3. **扩展性**: 设计是否便于扩展、是否支持插件化
4. **Kernel 使用**: 是否正确使用 Kernel 提供的能力
5. **状态管理**: 状态同步是否正确、是否有一致性问题
6. **集成测试**: 是否有充分的集成测试
7. **文档完整性**: 使用场景是否清晰、示例是否完整

**审查流程**:
```
PR 创建 → 自动化测试（5-10分钟）
    ↓
CI 通过 → 核心维护者审查（1-2天）
    ↓
代码 LGTM → 集成测试（如需要）
    ↓
全部通过 → 合并到主分支
```

### App 层 PR 审查

**自动检查**:
```bash
- pytest --cov=mofox_src/app --cov-report=term --cov-fail-under=80
- black --check mofox-src/app
- flake8 mofox-src/app
```

**人工审查重点**:
1. **用户体验**: 功能是否易用、配置是否合理
2. **插件兼容**: 是否影响现有插件、插件接口是否合理
3. **端到端测试**: 是否有完整的 E2E 测试
4. **文档清晰度**: 用户文档是否清晰

---

## 质量检查清单

### Kernel 层提交清单

#### 代码质量
- [ ] 遵循 PEP 8 规范
- [ ] 所有公共 API 有类型注解
- [ ] 所有公共 API 有文档字符串
- [ ] 错误处理完善
- [ ] 资源管理正确（使用 context manager）
- [ ] 无明显性能问题

#### 测试质量
- [ ] 测试覆盖率 = 100%
- [ ] 包含单元测试
- [ ] 包含集成测试（如适用）
- [ ] 测试边界情况
- [ ] 测试异常情况
- [ ] 测试并发场景（如适用）
- [ ] 所有测试通过

#### 文档质量
- [ ] 有对应的 .md 文档文件
- [ ] 文档包含概述
- [ ] 文档包含所有公共 API 说明
- [ ] 文档包含使用示例
- [ ] 文档包含注意事项
- [ ] 示例代码可运行

#### 兼容性
- [ ] API 变更向后兼容
- [ ] 或提供迁移指南
- [ ] 版本号更新合理

#### 性能
- [ ] 无明显性能回归
- [ ] 有性能测试（如适用）
- [ ] 内存使用合理

### Core 层提交清单

#### 代码质量
- [ ] 遵循 PEP 8 规范
- [ ] 所有公共 API 有类型注解
- [ ] 所有公共 API 有文档字符串
- [ ] 错误处理完善
- [ ] 模块依赖合理

#### 测试质量
- [ ] 测试覆盖率 = 100%
- [ ] 包含单元测试
- [ ] 包含集成测试
- [ ] 所有测试通过

#### 文档质量
- [ ] 有对应的 .md 文档文件
- [ ] 文档包含使用场景说明
- [ ] 文档包含示例代码
- [ ] 示例代码可运行

#### 设计质量
- [ ] 正确使用 Kernel 能力
- [ ] 模块职责清晰
- [ ] 便于扩展

---

## 开发工具推荐

### IDE 设置

**VSCode 推荐插件**:
- Python
- Pylance
- Python Test Explorer
- GitLens
- Better Comments
- Code Spell Checker

**VSCode 设置** (`.vscode/settings.json`):
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

### Git Hooks

使用 pre-commit 自动检查：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 hooks
pre-commit install
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        files: ^mofox_src/(kernel|core)/
```

---

## 常见问题

### Q: Kernel 层 100% 覆盖率是否太严格？

A: Kernel 层是整个系统的基础，质量要求必须最高。100% 覆盖率能够：
- 确保基础功能稳定可靠
- 避免底层 bug 影响上层功能
- 便于重构和维护
- 提供使用示例和文档

### Q: 如何处理无法测试的代码？

A: 通过依赖注入、Mock 等方式使代码可测试。如果确实无法测试，使用 `# pragma: no cover` 标记并在注释中说明原因。

### Q: PR 审查需要多久？

A: 
- Kernel 层：通常 3-5 个工作日
- Core 层：通常 1-3 个工作日
- App 层：通常 1-2 个工作日

紧急修复会加快审查速度。

### Q: 文档写多详细合适？

A: 至少包含：功能说明、API 参考、使用示例、注意事项。如果是复杂模块，还应包含工作原理、设计决策等。

---

## 获取帮助

- 📖 查看 [文档中心](docs/README.md)
- 💬 在 GitHub Discussions 提问
- 🐛 在 GitHub Issues 报告 bug
- 📧 联系维护者团队

---

## 致谢

感谢所有为 MoFox 项目做出贡献的开发者！

---

*最后更新: 2026年1月1日*
