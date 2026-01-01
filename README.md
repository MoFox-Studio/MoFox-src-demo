# MoFox 重构概览

> 说明：本文件仅提供分层和目录的框架性概览，暂未包含具体实现或使用示例，可结合 [MoFox 重构指导总览.md](MoFox%20重构指导总览.md) 查看更详细的设计描述。

## 分层设计
- **kernel**：与具体业务无关的基础能力，包括配置、数据库、向量库、LLM 请求、日志、并发、存储等。
- **core**：使用 kernel 能力实现记忆、对话、行为等核心功能，不关心插件或具体平台。
- **app**：把 kernel 与 core 组装成可运行的 Bot 系统，对外暴露高级 API 与插件扩展点（当前文档未详细展开）。

## 目录速览
```
mofox-src/
  kernel/
  core/
```

## kernel 模块一览
- **db**：数据库接口与核心（dialect 适配、engine、session、异常）；优化模块含多级缓存（cache backend/local/redis 与 cache_manager）；API 提供 CRUD 与 Query 入口。
- **vector_db**：向量存储抽象与 chromadb 实现，入口工厂初始化服务实例。
- **config**：配置基类与读取、修改、更新的实现。
- **llm**：LLM 请求系统（utils、llm_request、异常、client 注册）；clients 包含 base、aiohttp gemini、bedrock、openai；payload 包含 message、resp_format、tool_option、standard_prompt。
- **logger**：日志入口、清理、元数据、格式化器、配置与处理器（console/file）。
- **concurrency**：异步任务管理与全局 watchdog。
- **storage**：JSON 本地持久化操作器。

## core 模块一览
- **components**：
  - base 组件基类：action、adapter、chatter、command、event_handler、router、service、plugin、prompt、tool。
  - managers：action/adapter/chatter/event/service/permission/plugin/prompt_component 管理器；MCP 管理（client/tool）；tool 管理（history、use）。
  - registry：组件注册；state_manager：组件状态管理；types：组件类型定义。
- **prompt**：Prompt 基类、全局管理器、参数系统。
- **perception**：感知学习，含 memory/knowledge/meme/express 等子模块。
- **transport**：通讯传输，含 message_receive、message_send、router、sink（针对适配器与 WS）。
- **models**：基础模型入口。

## 开发规范与质量要求

### 强制性规范（kernel & core 层）

#### 1. 测试覆盖率要求
- **kernel 层和 core 层必须达到 100% pytest 测试覆盖率**
- 每个模块文件必须有对应的独立测试文件
- 测试文件命名规范：`test_<module_name>.py`
- 测试位置：与源码目录结构对应的 `tests/` 目录下

#### 2. 测试文件结构要求
```
mofox-src/
├── kernel/
│   ├── concurrency/
│   │   ├── watchdog.py
│   │   └── task_manager.py
│   └── ...
└── tests/
    ├── kernel/
    │   ├── concurrency/
    │   │   ├── test_watchdog.py
    │   │   └── test_task_manager.py
    │   └── ...
    └── core/
        └── ...
```

#### 3. 文档要求
- 每个模块文件必须有对应的 Markdown 文档
- 文档命名规范：与模块文件同名，扩展名为 `.md`
- 文档位置：`docs/` 目录下，保持与源码相同的目录结构
- 文档内容必须包含：
  - 模块功能概述
  - 主要类/函数说明
  - 使用示例
  - API 参考
  - 依赖关系说明

#### 4. 文档结构示例
```
docs/
├── kernel/
│   ├── concurrency/
│   │   ├── watchdog.md
│   │   └── task_manager.md
│   └── ...
└── core/
    └── ...
```

#### 5. 测试规范
- 单元测试：测试独立函数和方法
- 集成测试：测试模块间协作
- 异步测试：使用 `pytest-asyncio` 测试异步代码
- Mock 测试：使用 `pytest-mock` 隔离外部依赖
- 覆盖率检查：运行 `pytest --cov=mofox_src --cov-report=html`

#### 6. 代码质量检查
所有提交必须通过以下检查：
```bash
# 代码格式化
black mofox-src/

# 代码风格检查
flake8 mofox-src/

# 类型检查
mypy mofox-src/

# 导入排序
isort mofox-src/

# 运行测试
pytest tests/ --cov=mofox_src --cov-report=term-missing
```

#### 7. 提交前检查清单
- [ ] 代码已通过所有单元测试
- [ ] 测试覆盖率达到 100%
- [ ] 已编写模块文档
- [ ] 代码已格式化（black）
- [ ] 已通过 flake8 检查
- [ ] 已通过 mypy 类型检查
- [ ] 文档示例代码已验证可运行

### 推荐开发流程

1. **编写接口和类型定义** - 先定义清晰的接口
2. **编写文档** - 描述预期行为和使用方式
3. **编写测试用例** - TDD（测试驱动开发）
4. **实现功能代码** - 让测试通过
5. **代码审查** - 确保符合规范
6. **提交代码** - 附带测试和文档

### 质量目标

- **kernel 层**：零依赖外部业务逻辑，100% 可复用
- **core 层**：最小化对 kernel 的耦合，清晰的抽象边界
- **测试覆盖率**：kernel & core 层保持 100%
- **文档完整性**：每个公开 API 都有文档和示例
- **代码可维护性**：新人可通过文档快速上手

