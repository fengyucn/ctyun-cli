# ctyun-cli 项目规则和配置文档

## 项目概述

**项目名称：** ctyun-cli
**项目类型：** 天翼云CLI工具 - 基于终端的云资源管理平台
**当前版本：** v1.3.10
**维护者：** Ctyun CLI Team

## 项目路径结构

### 核心路径规则

```
/home/fengyu/devhome/hxctbox/ctyun_cli/          # 主项目根目录
├── src/                                          # 源代码目录
│   ├── cli/main.py                              # 主CLI入口点
│   ├── client.py                                # 基础客户端
│   ├── redis/                                   # Redis模块（新增）
│   ├── auth/                                    # 认证模块
│   └── [其他服务模块]/
├── dist/                                         # PyPI分发包（构建时生成）
├── tests/                                        # 测试文件
├── docs/                                         # 文档目录
└── setup.py                                     # 包构建配置

/home/fengyu/devhome/hxctbox/todoapi/             # API文档目录
├── Redis分布式缓存API/                          # Redis API文档
└── [其他API文档]/
```

### Git仓库规则

- **仓库根目录：** `/home/fengyu/devhome/hxctbox/ctyun_cli`
- **远程仓库：** `git@github.com:fengyucn/ctyun-cli.git`
- **主分支：** `master`
- **工作目录：** 所有开发工作在`ctyun_cli`目录下进行

### .gitignore 规则

```gitignore
# API文档目录（重要：todoapi目录必须排除）
todoapi/

# 构建产物
dist/
build/
*.egg-info/

# Python缓存
__pycache__/
*.py[cod]
*$py.class

# 测试缓存
.pytest_cache/
.coverage

# 环境变量
.env
```

## 开发规则

### 代码组织原则

1. **SOLID原则：**
   - **单一职责：** 每个类/函数只负责一个明确的功能
   - **开闭原则：** 对扩展开放，对修改封闭
   - **接口隔离：** 接口专一，避免"胖接口"
   - **依赖倒置：** 依赖抽象而非具体实现

2. **KISS原则：** 追求代码和设计的极致简洁

3. **DRY原则：** 避免代码重复，主动抽象和复用

4. **YAGNI原则：** 仅实现当前明确所需的功能

### 模块集成规则

1. **新服务模块标准结构：**
   ```
   src/[service_name]/
   ├── __init__.py           # 导出主要类和函数
   ├── client.py            # API客户端实现
   └── commands.py          # CLI命令定义
   ```

2. **主CLI集成：**
   - 在`src/cli/main.py`中导入新模块命令组
   - 使用`cli.add_command()`注册命令组
   - 遵循Click框架最佳实践

3. **认证集成：**
   - 必须使用`src/auth/eop_signature.py`中的`CTYUNEOPAuth`类
   - 复用`src/client.py`中的`CTYUNClient`基础设施
   - 不得实现独立的认证逻辑

### 危险操作确认机制

执行以下操作前必须获得明确确认：

**高风险操作：**
- 文件系统：删除文件/目录、批量修改、移动系统文件
- 代码提交：`git commit`、`git push`、`git reset --hard`
- 系统配置：修改环境变量、系统设置、权限变更
- 数据操作：数据库删除、结构变更、批量更新
- 网络请求：发送敏感数据、调用生产环境API
- 包管理：全局安装/卸载、更新核心依赖

**确认格式：**
```
⚠️ 危险操作检测！
操作类型：[具体操作]
影响范围：[详细说明]
风险评估：[潜在后果]

请确认是否继续？[需要明确的"是"、"确认"、"继续"]
```

## 命令执行标准

### 路径处理规则
- 始终使用双引号包裹文件路径
- 优先使用正斜杠 `/` 作为路径分隔符
- 跨平台兼容性检查

### 工具优先级
1. `rg` (ripgrep) > `grep` 用于内容搜索
2. 专用工具 (Read/Write/Edit) > 系统命令
3. 批量工具调用提高效率

### 开发工作流

1. **开发前：**
   ```bash
   cd /home/fengyu/devhome/hxctbox/ctyun_cli
   git status
   ```

2. **代码提交：**
   ```bash
   git add .
   git commit -m "描述性提交信息"
   git push origin master
   ```

3. **包构建：**
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```

4. **包发布：**
   ```bash
   # 先测试环境
   twine upload --repository testpypi dist/*
   # 后正式环境
   twine upload dist/*
   ```

## 版本管理规则

### 语义化版本控制

**版本格式：** `主版本.次版本.修订版本` (如 1.3.0)

- **主版本：** 不兼容的API修改
- **次版本：** 向后兼容的功能性新增
  - 新增服务模块（如Redis模块）
  - 重要的功能增强
- **修订版本：** 向后兼容的问题修正

### 版本更新流程

1. 更新`setup.py`中的版本号
2. 更新描述和关键词
3. 重新构建分发包
4. 先发布到TestPyPI测试
5. 确认无误后发布到正式PyPI

## 配置管理

### 用户配置文件

**位置：** `~/.ctyun/config`
**格式：** INI格式
```ini
[default]
access_key = your_access_key
secret_key = your_secret_key
region = 200000001852
endpoint = https://api.ctyun.cn
timeout = 30
retry = 3
output_format = table

[HX]
access_key = 8199e3911a794a2587dfb7764601d4e0
secret_key = 0421ff3125fb42c182bfc732bf4dbf76
region = 1
```

### 配置使用规则

1. 优先使用`ctyun-cli configure`命令进行配置
2. 支持多配置文件（使用`--profile`参数）
3. 命令行参数优先级高于配置文件
4. 敏感信息不得硬编码在源代码中

## API集成规则

### Redis模块集成示例

**成功案例：**
- ✅ 使用现有EOP认证系统
- ✅ 集成到configure模块
- ✅ 提供多种输出格式（table、json、summary）
- ✅ 支持多区域批量查询
- ✅ 完整的错误处理机制

**API调用模式：**
```python
# 正确的客户端继承模式
class RedisClient:
    def __init__(self, access_key: str, secret_key: str, region_id: str = "200000001852"):
        self.client = CTYUNClient(access_key, secret_key)
        self.eop_auth = CTYUNEOPAuth(access_key, secret_key)
```

## 部署规则

### 发布检查清单

- [ ] 代码已提交到GitHub
- [ ] 版本号已更新
- [ ] 构建无警告和错误
- [ ] TestPyPI发布成功
- [ ] 测试环境验证通过
- [ ] PyPI正式发布完成
- [ ] 文档已更新

### 分发包规则

1. **必须包含：**
   - 所有源代码
   - README文档
   - LICENSE文件
   - requirements.txt
   - setup.py配置

2. **必须排除：**
   - API文档目录（todoapi/）
   - 开发缓存文件
   - 测试覆盖率报告
   - 本地配置文件

## 故障排查

### 常见问题解决方案

1. **Git问题：**
   ```bash
   # 检查Git状态
   git status

   # 重新配置远程仓库
   git remote set-url origin git@github.com:fengyucn/ctyun-cli.git
   ```

2. **构建问题：**
   ```bash
   # 清理构建缓存
   rm -rf dist/ build/ *.egg-info
   python -m build --verbose
   ```

3. **认证问题：**
   ```bash
   # 检查配置
   ctyun-cli show-config

   # 重新配置
   ctyun-cli configure --access-key KEY --secret-key SECRET
   ```

## 安全规则

### 敏感信息处理

1. **禁止：**
   - 在源代码中硬编码API密钥
   - 在Git提交中包含配置文件
   - 在日志中输出敏感信息

2. **必须：**
   - 使用配置文件管理凭证
   - 将敏感目录加入.gitignore
   - 实现适当的权限控制

### API调用安全

- 使用HTTPS进行所有API通信
- 实现请求超时控制
- 提供重试机制
- 验证服务器证书

## 文档规则

### 文档维护

1. **必须维护：**
   - README.md（项目介绍）
   - [SERVICE]_USAGE.md（各模块使用说明）
   - PROJECT_RULES.md（本文档）

2. **更新时机：**
   - 新模块发布时
   - 重大功能更新时
   - API变更时

### 代码注释规范

- 使用中文注释
- 复杂逻辑必须有详细说明
- API接口必须有docstring
- 遵循Google Python风格指南

---

**文档更新时间：** 2025-11-24
**适用版本：** v1.3.10+
**维护责任：** 项目维护者

**重要提醒：**
- 所有操作必须遵循本文档规则
- devhome/hxctbox/ctyun_cli 是唯一正确的工作目录
- todoapi目录永远不进入Git仓库