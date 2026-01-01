# MoFox 文档中心

本目录包含 MoFox 项目的完整文档，文档结构与源码目录一一对应。

## 📚 文档结构

```
docs/
├── kernel/              # Kernel 层文档 - 基础能力
│   ├── concurrency/     # 并发管理
│   │   ├── watchdog.md
│   │   └── task_manager.md
│   ├── config/          # 配置系统
│   ├── db/              # 数据库模块
│   │   ├── core/        # 数据库核心
│   │   ├── optimization/ # 数据库优化
│   │   └── api/         # 数据库 API
│   ├── llm/             # LLM 请求系统
│   │   ├── model_client/ # 模型客户端
│   │   └── payload/     # 请求负载
│   ├── logger/          # 日志系统
│   ├── storage/         # 本地存储
│   └── vector_db/       # 向量数据库
│
└── core/                # Core 层文档 - 核心功能
    ├── components/      # 组件系统
    │   ├── base/        # 基础组件
    │   └── managers/    # 组件管理器
    │       ├── mcp_manager/
    │       └── tool_manager/
    ├── models/          # 数据模型
    ├── perception/      # 感知学习
    │   ├── express/
    │   ├── knowledge/
    │   ├── meme/
    │   └── memory/
    ├── prompt/          # Prompt 系统
    └── transport/       # 通讯传输
        ├── message_receive/
        ├── message_send/
        ├── router/
        └── sink/
```

## 📖 文档规范

每个模块文档应包含：

1. **模块概述** - 功能描述和设计目标
2. **核心组件** - 主要类、函数、常量的说明
3. **使用示例** - 实际代码示例
4. **API 参考** - 详细的参数和返回值说明
5. **依赖关系** - 与其他模块的关系
6. **注意事项** - 使用限制和最佳实践

## 🔍 快速导航

### Kernel 层（基础能力）

#### 并发管理
- [Watchdog 全局任务监控器](kernel/concurrency/watchdog.md) - 异步任务监控和管理

#### 配置系统
- 配置项基类 - 待完善
- 配置读取与更新 - 待完善

#### 数据库模块
- 数据库引擎 - 待完善
- 会话管理 - 待完善
- 多级缓存 - 待完善
- CRUD API - 待完善

#### LLM 系统
- LLM 请求核心 - 待完善
- 客户端注册 - 待完善
- 标准负载构建 - 待完善

#### 日志系统
- 日志核心 - 待完善
- 日志处理器 - 待完善
- 日志清理 - 待完善

#### 存储系统
- JSON 持久化 - 待完善

#### 向量数据库
- 向量存储抽象 - 待完善
- ChromaDB 实现 - 待完善

### Core 层（核心功能）

#### 组件系统
- 组件基类 - 待完善
- 组件管理器 - 待完善
- MCP 管理 - 待完善
- 工具管理 - 待完善

#### Prompt 系统
- Prompt 管理器 - 待完善
- 参数系统 - 待完善

#### 感知学习
- 记忆系统 - 待完善
- 知识系统 - 待完善
- 表达系统 - 待完善

#### 通讯传输
- 消息接收 - 待完善
- 消息发送 - 待完善
- 路由系统 - 待完善

## 📝 文档编写指南

### 文档命名规范
- 文档文件名与对应的 Python 模块文件同名
- 扩展名为 `.md`
- 例如：`watchdog.py` → `watchdog.md`

### 目录结构规范
- 文档目录结构与源码目录结构完全一致
- 例如：`mofox-src/kernel/concurrency/watchdog.py` → `docs/kernel/concurrency/watchdog.md`

### 内容编写规范

#### 标题层级
```markdown
# 模块名称（一级标题）

## 概述（二级标题）

### 功能特性（三级标题）

#### 具体功能点（四级标题）
```

#### 代码示例
使用代码块，并指定语言：
````markdown
```python
# 示例代码
import asyncio
```
````

#### API 文档
```markdown
**`function_name(param1, param2) -> ReturnType`**

功能描述

参数:
- `param1` (type): 参数说明
- `param2` (type): 参数说明

返回:
- `ReturnType`: 返回值说明

示例:
    代码示例
```

## 🚀 贡献文档

欢迎为 MoFox 项目贡献文档！

### 步骤
1. 选择一个待完善的模块
2. 在对应目录创建 `.md` 文件
3. 按照文档规范编写内容
4. 更新本 README 的快速导航链接

### 质量要求
- 内容准确、清晰
- 包含实际可运行的示例代码
- 说明模块的设计意图和使用场景
- 标注注意事项和最佳实践

## 📊 文档完成度

### Kernel 层
- [x] concurrency/watchdog.py - 已完成
- [ ] concurrency/task_manager.py
- [ ] config/*
- [ ] db/*
- [ ] llm/*
- [ ] logger/*
- [ ] storage/*
- [ ] vector_db/*

### Core 层
- [ ] components/*
- [ ] models/*
- [ ] perception/*
- [ ] prompt/*
- [ ] transport/*

---

*最后更新: 2026年1月1日*
