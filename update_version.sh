#!/bin/bash

# 版本号更新脚本
# 用法: ./update_version.sh [新版本号]
# 例如: ./update_version.sh 1.3.11

set -e  # 遇到错误立即退出

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供新版本号"
    echo "用法: $0 <新版本号>"
    echo "例如: $0 1.3.11"
    exit 1
fi

NEW_VERSION="$1"
OLD_VERSION_PATTERN="[0-9]+\.[0-9]+\.[0-9]+"

echo "🔄 开始更新版本号到: $NEW_VERSION"
echo "================================"

# 备份当前状态
echo "📦 创建备份..."
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp pyproject.toml "$backup_dir/"
cp setup.py "$backup_dir/"
cp src/ctyun_cli/__init__.py "$backup_dir/"
cp README.md "$backup_dir/"
cp README_EN.md "$backup_dir/"
echo "✅ 备份已保存到: $backup_dir"

# 更新核心配置文件
echo "🔧 更新核心配置文件..."

sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "✅ 更新 pyproject.toml"

sed -i "s/version=\".*\",/version=\"$NEW_VERSION\",/" setup.py
echo "✅ 更新 setup.py"

sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/ctyun_cli/__init__.py
echo "✅ 更新 src/ctyun_cli/__init__.py"

# 更新文档
echo "📚 更新文档..."

sed -i "s/\*\*当前版本：\** $OLD_VERSION_PATTERN (Latest)/**当前版本：** $NEW_VERSION (Latest)/" README.md
echo "✅ 更新 README.md 当前版本"

sed -i "s/\*\*Current Version:\*\* $OLD_VERSION_PATTERN/**Current Version:** $NEW_VERSION/" README_EN.md
echo "✅ 更新 README_EN.md 当前版本"

sed -i "s/- \*\*CLI版本\*\*: v$OLD_VERSION_PATTERN+/- **CLI版本**: v$NEW_VERSION+/" REDIS_CREATE_INSTANCE.md
echo "✅ 更新 REDIS_CREATE_INSTANCE.md"

sed -i "s/\*\*当前版本：\** v$OLD_VERSION_PATTERN/**当前版本：** v$NEW_VERSION/" PROJECT_RULES.md
echo "✅ 更新 PROJECT_RULES.md (第1处)"

sed -i "s/\*\*适用版本：\** v$OLD_VERSION_PATTERN+/**适用版本：** v$NEW_VERSION+/" PROJECT_RULES.md
echo "✅ 更新 PROJECT_RULES.md (第2处)"

sed -i "s/\*\*当前版本\*\*: $OLD_VERSION_PATTERN/**当前版本**: $NEW_VERSION/" PROJECT_SUMMARY.md
echo "✅ 更新 PROJECT_SUMMARY.md (第1处)"

sed -i "s/当前版本（$OLD_VERSION_PATTERN）/当前版本（$NEW_VERSION）/" PROJECT_SUMMARY.md
echo "✅ 更新 PROJECT_SUMMARY.md (第2处)"

# 验证更新结果
echo "🔍 验证更新结果..."

echo ""
echo "=== 核心配置文件版本 ==="
grep "version = " pyproject.toml
grep "version=" setup.py
grep "__version__" src/ctyun_cli/__init__.py

echo ""
echo "=== 文档版本 ==="
echo "README.md:" && grep "当前版本：" README.md
echo "README_EN.md:" && grep "Current Version:" README_EN.md

echo ""
echo "=== 其他文档 ==="
echo "PROJECT_RULES.md:" && grep "当前版本：" PROJECT_RULES.md | head -1
echo "PROJECT_SUMMARY.md:" && grep "当前版本" PROJECT_SUMMARY.md | head -1

# 检查是否还有遗漏的旧版本号
echo ""
echo "🔍 检查遗漏的版本引用..."
old_version_refs=$(grep -r "1\.3\.[0-9]" . --include="*.py" --include="*.md" --include="*.toml" --include="*.txt" -n | grep -v "$NEW_VERSION" | grep -v "1\.3\.9" || true)

if [ -n "$old_version_refs" ]; then
    echo "⚠️  发现可能遗漏的版本引用:"
    echo "$old_version_refs"
    echo ""
    echo "请检查上述文件中的版本号是否需要更新"
else
    echo "✅ 没有发现遗漏的版本引用"
fi

echo ""
echo "🎉 版本号更新完成！"
echo "================================"
echo "新版本: $NEW_VERSION"
echo "备份位置: $backup_dir"
echo ""
echo "📋 后续步骤:"
echo "1. 在 README.md 中添加新版本更新说明"
echo "2. 运行 'python -m build' 验证构建"
echo "3. 运行 'pip install -e .' 测试安装"
echo "4. 提交代码到版本控制系统"
echo ""
echo "💡 快速添加版本说明模板:"
echo "**重大更新 v$NEW_VERSION - 功能名称：**"
echo "- 🔥 **新功能描述1** - 详细说明"
echo "- ✨ **新功能描述2** - 详细说明"
echo "- 🔧 **改进说明3** - 详细说明"