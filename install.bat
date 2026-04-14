@echo off
REM Agile-Agent Hub 快速安装脚本
REM 适用于 Windows

echo ==========================================
echo   Agile-Agent Hub 快速安装
echo ==========================================
echo.

REM 检查 Python
echo [1/8] 检查 Python 版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python 3.12+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%

REM 创建虚拟环境
echo.
echo [2/8] 创建 Python 虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✅ 虚拟环境已创建
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo [3/8] 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✅ 虚拟环境已激活

REM 升级 pip
echo.
echo [4/8] 升级 pip...
python -m pip install --upgrade pip
echo ✅ pip 已升级

REM 安装主项目依赖
echo.
echo [5/8] 安装主项目依赖...
pip install -e .
echo ✅ 主项目依赖已安装

REM 安装 NcatBot 依赖
echo.
echo [6/8] 安装 NcatBot 依赖...
cd NcatBot
pip install -e .[test]
cd ..
echo ✅ NcatBot 依赖已安装

REM 链接插件
echo.
echo [7/8] 复制插件到 NcatBot...
cd NcatBot
if not exist "plugins" mkdir plugins
if not exist "plugins\agile_agent_hub" (
    xcopy /E /I /Y "..\plugins\agile_agent_hub" "plugins\agile_agent_hub"
    echo ✅ 插件已复制
) else (
    echo ✅ 插件已存在
)
cd ..

REM 运行测试
echo.
echo [8/8] 运行测试...
cd plugins\agile_agent_hub
python tests\test_defensive_utils.py
python tests\test_integration.py
cd ..\..

echo.
echo ==========================================
echo   ✅ 安装完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 安装并启动 NapCat (https://napneko.github.io/)
echo 2. 编辑 NcatBot\config.yaml 填入您的配置
echo 3. 编辑 plugins\agile_agent_hub\config.yaml 填入 LLM API Key
echo 4. 启动 NcatBot：
echo    cd NcatBot
echo    ..\venv\Scripts\activate.bat
echo    python -m ncatbot.cli.main run
echo.
echo 详细说明请参考：
echo   - INSTALLATION_GUIDE.md (完整安装指南)
echo   - QQ_TEST_GUIDE.md (QQ 测试指南)
echo.
pause

