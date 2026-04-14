#!/bin/bash
# Agile-Agent Hub 快速安装脚本
# 适用于 macOS 和 Linux

set -e

echo "=========================================="
echo "  Agile-Agent Hub 快速安装"
echo "=========================================="
echo ""

# 检查 Python
echo "[1/8] 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.12+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python 版本: $PYTHON_VERSION"

REQUIRED_VERSION="3.12"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 版本过低，需要 3.12+"
    exit 1
fi

# 创建虚拟环境
echo ""
echo "[2/8] 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "[3/8] 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 升级 pip
echo ""
echo "[4/8] 升级 pip..."
pip install --upgrade pip
echo "✅ pip 已升级"

# 安装主项目依赖
echo ""
echo "[5/8] 安装主项目依赖..."
pip install -e .
echo "✅ 主项目依赖已安装"

# 安装 NcatBot 依赖
echo ""
echo "[6/8] 安装 NcatBot 依赖..."
cd NcatBot
pip install -e .[test]
cd ..
echo "✅ NcatBot 依赖已安装"

# 链接插件
echo ""
echo "[7/8] 链接插件到 NcatBot..."
cd NcatBot
mkdir -p plugins
if [ ! -L "plugins/agile_agent_hub" ]; then
    ln -sf ../../plugins/agile_agent_hub ./plugins/agile_agent_hub
    echo "✅ 插件已链接"
else
    echo "✅ 插件已链接"
fi
cd ..

# 运行测试
echo ""
echo "[8/8] 运行测试..."
cd plugins/agile_agent_hub
python tests/test_defensive_utils.py
python tests/test_integration.py
cd ../..

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 安装并启动 NapCat (https://napneko.github.io/)"
echo "2. 编辑 NcatBot/config.yaml 填入您的配置"
echo "3. 编辑 plugins/agile_agent_hub/config.yaml 填入 LLM API Key"
echo "4. 启动 NcatBot："
echo "   cd NcatBot"
echo "   source ../venv/bin/activate"
echo "   python -m ncatbot.cli.main run"
echo ""
echo "详细说明请参考："
echo "  - INSTALLATION_GUIDE.md (完整安装指南)"
echo "  - QQ_TEST_GUIDE.md (QQ 测试指南)"
echo ""

