# Claude AI 助手项目文档

## 项目概述

**天翼云CLI工具** 是一款功能强大的企业级命令行工具，支持天翼云资源的终端管理。

### 项目统计
- 📊 **代码规模**: 15,000+行代码
- 🔧 **API覆盖**: 156+个API接口
- ⚡ **命令数量**: 136+个CLI命令
- 🏗️ **服务模块**: 7大核心服务模块

## 重要文档位置

### 🏗️ 架构和规则文档
- **[Python模块创建规则](PYTHON_MODULE_RULES.md)** - Python项目模块创建和组织标准
- **[项目总结](PROJECT_SUMMARY.md)** - 项目整体架构和技术总结
- **[项目规则](PROJECT_RULES.md)** - 开发规范和约定

### 📚 使用文档
- **[README.md](README.md)** - 项目主要说明文档
- **[命令手册](COMMAND_MANUAL.md)** - 完整的CLI命令参考
- **[监控服务文档](MONITOR_USAGE.md)** - 54个监控API详细指南

### 🔧 服务模块文档
- **[Redis服务指南](REDIS_CLI_USAGE.md)** - 分布式缓存服务使用
- **[IAM服务指南](IAM_USAGE.md)** - 身份访问管理服务

## 项目结构

```
ctyun-cli/
├── src/                        # 源代码目录
│   ├── core/                   # 核心API客户端
│   ├── cli/                    # CLI命令入口
│   ├── ecs/                    # 云服务器服务
│   ├── monitor/                # 监控服务
│   ├── redis/                  # 分布式缓存服务
│   ├── billing/                # 计费服务
│   ├── security/               # 安全服务
│   ├── iam/                    # 身份访问管理
│   ├── ebs/                    # 弹性块存储
│   ├── auth/                   # 认证模块
│   ├── utils/                  # 工具函数
│   └── config/                 # 配置管理
├── tests/                      # 测试代码
├── docs/                       # 项目文档
├── examples/                   # 示例代码
└── dist/                       # 构建产物
```

## 模块开发指南

### 创建新模块的步骤

1. **遵循模块创建规则**: 参考 [Python模块创建规则](PYTHON_MODULE_RULES.md)
2. **添加必要的__init__.py**: 确保包目录结构完整
3. **使用正确的导入方式**:
   - 开发时: `from module import`
   - 包内: `from .module import`
4. **定义公共接口**: 通过`__all__`变量控制导出

### 核心模块说明

#### core模块
- `CTYUNClient`: API客户端基类
- `CTYUNAPIError`: API异常基类
- 所有服务模块的基础依赖

#### cli模块
- `main.py`: CLI入口点
- 使用Click框架构建命令行界面
- 支持多环境配置和调试模式

#### auth模块
- `signature.py`: 通用签名实现
- `eop_signature.py`: EOP签名算法
- 为API请求提供安全认证

## 开发约定

### 代码规范
- 遵循PEP 8代码风格
- 使用类型注解
- 完善的文档字符串
- 单一职责原则

### 导入规范
```python
# 标准库
import os
from typing import Optional

# 第三方库
import click
import requests

# 本地导入
from core import CTYUNClient
from utils.helpers import format_output
```

### 测试规范
- 测试文件以`test_`开头
- 使用pytest框架
- 保持高测试覆盖率

## 打包和发布

### 构建命令
```bash
python -m build --wheel --no-isolation
```

### 发布命令
```bash
# 测试PyPI
python -m twine upload --repository testpypi dist/*

# 生产PyPI
python -m twine upload dist/*
```

### 版本管理
- 版本号在 `pyproject.toml` 中定义
- 遵循语义化版本控制
- 每次发布前更新版本号

## 常见问题解决

### 导入错误
- 检查 `__init__.py` 文件是否完整
- 验证导入路径是否正确
- 确保包结构符合规范

### 打包问题
- 清理 `dist/` 目录后重新构建
- 检查 `pyproject.toml` 配置
- 验证所有必要文件已包含

### 安装测试
```bash
# 本地测试安装
pip install -e .

# 构建测试
python -m build
```

## 贡献指南

1. 遵循现有的代码风格和结构
2. 添加适当的测试覆盖
3. 更新相关文档
4. 确保所有测试通过
5. 提交前运行完整测试套件

## 联系信息

- **作者**: Y.FENG
- **邮箱**: popfrog@gmail.com
- **项目地址**: https://github.com/fengyucn/ctyun-cli
- **问题反馈**: https://github.com/fengyucn/ctyun-cli/issues

---

*本文档随项目更新持续维护*