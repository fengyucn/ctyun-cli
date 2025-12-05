# Claude Skills - 版本发布工作流

这是一个专门为ctyun-cli项目设计的自动化版本发布工作流。

## 🚀 功能特性

- ✅ **版本号管理**: 自动增量或指定版本号
- ✅ **Git操作**: 自动提交和推送代码
- ✅ **包构建**: 清理并构建wheel包
- ✅ **PyPI发布**: 自动发布到测试和生产PyPI
- ✅ **发布记录**: 保存发布历史记录
- ✅ **错误处理**: 完善的错误处理和回滚机制

## 📦 安装依赖

确保已安装以下依赖：

```bash
pip install build twine
```

## 🔧 使用方法

### 1. 自动增量版本号（推荐）

```bash
# 自动增量补丁版本 (1.6.3 → 1.6.4)
python skills/release_workflow.py --auto patch

# 自动增量次版本号 (1.6.3 → 1.7.0)
python skills/release_workflow.py --auto minor

# 自动增量主版本号 (1.6.3 → 2.0.0)
python skills/release_workflow.py --auto major
```

### 2. 指定版本号

```bash
# 发布指定版本号
python skills/release_workflow.py --version 1.7.0
```

### 3. 仅发布现有版本

```bash
# 不更新版本号，仅发布当前版本
python skills/release_workflow.py --release-only
```

### 4. 自定义提交信息

```bash
# 使用自定义提交信息
python skills/release_workflow.py --auto minor \
  --commit-message "feat: 新增XX功能"
```

### 5. 高级选项

```bash
# 跳过Git状态检查
python skills/release_workflow.py --auto minor --skip-git-check

# 指定项目根目录
python skills/release_workflow.py --auto minor --project-root /path/to/project
```

## 📋 完整流程示例

```bash
# 标准发布流程
python skills/release_workflow.py --auto minor

# 输出示例：
# 🚀 开始版本发布流程
# ==================================================
# 🔍 检查Git状态
# ✅ Git状态检查通过
# 📌 自动增量版本号: 1.6.3 → 1.7.0
# 🔄 更新版本号到: 1.7.0
# ✅ 更新版本号: pyproject.toml (1.6.3 → 1.7.0)
# ✅ 更新版本号: setup.py (1.6.3 → 1.7.0)
# ✅ 更新版本号: src/ctyun_cli/__init__.py (1.6.3 → 1.7.0)
# ✅ 版本号更新完成，修改了 3 个文件
# 🔄 Git提交操作
# ✅ Git提交成功
# 🔄 Git推送操作
# ✅ Git推送成功
# 🔨 构建包
# 🧹 清理构建文件
# ✅ 构建文件清理完成
# ✅ 构建成功: ctyun_cli-1.7.0-py3-none-any.whl
# 🧪 先发布到测试PyPI验证...
# ✅ 上传到测试PyPI成功
# 🔗 https://test.pypi.org/project/ctyun-cli/
# 🚀 发布到生产PyPI...
# ✅ 上传到生产PyPI成功
# 🔗 https://pypi.org/project/ctyun-cli/
# ==================================================
# 🎉 版本发布成功！v1.7.0
# 📦 PyPI: https://pypi.org/project/ctyun-cli/1.7.0/
# 🧪 测试PyPI: https://test.pypi.org/project/ctyun-cli/1.7.0/
# 📝 发布记录已保存: .release_history.json
```

## 📂 文件结构

工作流会更新以下文件中的版本号：

- `pyproject.toml` - 主版本号配置
- `setup.py` - 兼容性版本号配置
- `src/ctyun_cli/__init__.py` - Python包版本号

并生成以下文件：

- `dist/ctyun_cli-{version}-py3-none-any.whl` - 构建的wheel包
- `.release_history.json` - 发布历史记录

## 🔒 安全考虑

- 自动先发布到测试PyPI验证
- Git状态检查防止意外提交
- 完整的错误处理和回滚
- 发布记录追踪

## 🐛 故障排除

### 常见问题

1. **Git状态检查失败**
   ```bash
   # 解决：先提交或暂存未提交的更改
   git status
   git add .
   git commit -m "保存未提交的更改"
   ```

2. **构建失败**
   ```bash
   # 解决：安装构建依赖
   pip install build
   ```

3. **PyPI上传失败**
   ```bash
   # 解决：检查PyPI凭据
   python -m twine check dist/*
   ```

## 📚 扩展功能

这个工作流可以轻松扩展到其他Python项目：

1. 复制 `skills/release_workflow.py` 到新项目
2. 修改文件路径和包名配置
3. 根据需要调整版本号模式

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工作流！

---

**注意**: 首次使用前请确保已配置好PyPI上传凭据：

```bash
# 配置PyPI凭据
python -m twine configure
```

或者设置环境变量：

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-token
```