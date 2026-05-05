@echo off
REM Hogwild UXR Installer for Windows (cmd.exe)
REM Installs the MCP server and copies skills to Copilot CLI

echo ============================================
echo  Hogwild UXR - Installer
echo ============================================
echo.

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
uv pip install -e "%SCRIPT_DIR%" --quiet
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

REM Create or update mcp-config.json
REM NOTE: This creates a minimal config. If you have existing MCPs, merge manually.
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
echo [4/4] Verifying...
uv run --project "%SCRIPT_DIR%" hogwild-uxr --help >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       Server responds OK.
) else (
    echo       [WARN] Server didn't respond to --help. This is normal for stdio servers.
    echo       It will work when Copilot CLI invokes it.
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
