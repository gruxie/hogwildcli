@echo off
REM Hogwild UXR Installer for Windows (cmd.exe)
REM Installs the MCP server and copies skills to Copilot CLI

echo ============================================
echo  Hogwild UXR - Installer
echo ============================================
echo.

REM Check for Python 3.10+
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo Install Python 3.10+: https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    if %%a LSS 3 (
        echo [ERROR] Python 3.10+ required, found %PY_VER%
        exit /b 1
    )
    if %%a EQU 3 if %%b LSS 10 (
        echo [ERROR] Python 3.10+ required, found %PY_VER%
        exit /b 1
    )
)

REM Check for uv
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] uv is not installed or not on PATH.
    echo Install it: pip install uv
    echo Or: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

REM Get the directory this script lives in
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo [1/4] Installing MCP server package...
uv sync --project "%SCRIPT_DIR%" --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install package.
    exit /b 1
)
echo       Done.

echo.
echo [2/4] Copying skills to ~/.copilot/skills/ ...
set "SKILLS_DEST=%USERPROFILE%\.copilot\skills"
if not exist "%SKILLS_DEST%" mkdir "%SKILLS_DEST%"

for /D %%d in ("%SCRIPT_DIR%\skills\uxr-*") do (
    set "SKILL_NAME=%%~nxd"
    xcopy "%%d" "%SKILLS_DEST%\%%~nxd\" /E /I /Y /Q >nul
)
echo       Done. Skills installed to %SKILLS_DEST%

echo.
echo [3/4] Registering MCP server in Copilot CLI config...
set "MCP_CONFIG=%USERPROFILE%\.copilot\mcp-config.json"

REM Find uv path
for /f "delims=" %%i in ('where uv') do set "UV_PATH=%%i"

REM Back up existing config if present
if exist "%MCP_CONFIG%" (
    copy /y "%MCP_CONFIG%" "%MCP_CONFIG%.bak" >nul
    echo       Backed up existing config to mcp-config.json.bak
)

REM Create or update mcp-config.json
REM NOTE: This creates a minimal config. If you have existing MCPs, merge from .bak.
echo {> "%MCP_CONFIG%"
echo   "mcpServers": {>> "%MCP_CONFIG%"
echo     "hogwild-uxr": {>> "%MCP_CONFIG%"
echo       "command": "%UV_PATH:\=\\%",>> "%MCP_CONFIG%"
echo       "args": ["run", "--project", "%SCRIPT_DIR:\=\\%", "hogwild-uxr"]>> "%MCP_CONFIG%"
echo     }>> "%MCP_CONFIG%"
echo   }>> "%MCP_CONFIG%"
echo }>> "%MCP_CONFIG%"
echo       Done. Config at %MCP_CONFIG%

echo.
echo [4/4] Verifying server starts...
start "" /b uv run --project "%SCRIPT_DIR%" hogwild-uxr
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq hogwild-uxr.exe" 2>nul | find /i "hogwild-uxr" >nul
if %ERRORLEVEL% equ 0 (
    echo       Server verified OK.
    taskkill /f /im hogwild-uxr.exe >nul 2>&1
) else (
    echo       [ERROR] Server failed to start. Check that Python 3.10+ is installed.
    exit /b 1
)

echo.
echo ============================================
echo  Installation complete!
echo ============================================
echo.
echo  MCP server: hogwild-uxr (19 tools)
echo  Skills:     14 skills in %SKILLS_DEST%
echo  Config:     %MCP_CONFIG%
echo.
echo  Next steps:
echo    1. Restart Copilot CLI
echo    2. Run: /skills list   (should show uxr-* skills)
echo    3. Create a project folder with research_config.yaml
echo    4. Say: "Run the full analysis on my transcripts"
echo.
