#!/usr/bin/env bash
# Hogwild UXR Installer for macOS/Linux
# Installs the MCP server and copies skills to Copilot CLI

set -e

echo "============================================"
echo " Hogwild UXR - Installer"
echo "============================================"
echo ""

# Check for Python 3.10+
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed."
    echo "Install Python 3.10+: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "[ERROR] Python 3.10+ required, found $PY_VERSION"
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "[ERROR] uv is not installed."
    echo "Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Installing MCP server package..."
if ! uv sync --project "$SCRIPT_DIR" --quiet; then
    echo "      [ERROR] Failed to install package. Check uv and Python 3.10+ are working."
    exit 1
fi
echo "      Done."

echo ""
echo "[2/4] Copying skills to ~/.copilot/skills/ ..."
SKILLS_DEST="$HOME/.copilot/skills"
mkdir -p "$SKILLS_DEST"

for skill_dir in "$SCRIPT_DIR"/skills/uxr-*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$SKILLS_DEST/$skill_name"
    cp -r "$skill_dir"* "$SKILLS_DEST/$skill_name/"
done
echo "      Done. Skills installed to $SKILLS_DEST"

echo ""
echo "[3/4] Registering MCP server in Copilot CLI config..."
MCP_CONFIG="$HOME/.copilot/mcp-config.json"
UV_PATH=$(which uv)

# Back up existing config if present
if [ -f "$MCP_CONFIG" ]; then
    cp "$MCP_CONFIG" "$MCP_CONFIG.bak"
    echo "      Backed up existing config to mcp-config.json.bak"
fi

cat > "$MCP_CONFIG" << EOF
{
  "mcpServers": {
    "hogwild-uxr": {
      "command": "$UV_PATH",
      "args": ["run", "--project", "$SCRIPT_DIR", "hogwild-uxr"]
    }
  }
}
EOF
echo "      Done. Config at $MCP_CONFIG"

echo ""
echo "[4/4] Verifying server starts..."
uv run --project "$SCRIPT_DIR" hogwild-uxr &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "      Server verified OK."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
else
    echo "      [ERROR] Server failed to start. Check that Python 3.10+ is installed."
    exit 1
fi

echo ""
echo "============================================"
echo " Installation complete!"
echo "============================================"
echo ""
echo " MCP server: hogwild-uxr (19 tools)"
echo " Skills:     14 skills in $SKILLS_DEST"
echo " Config:     $MCP_CONFIG"
echo ""
echo " Next steps:"
echo "   1. Restart Copilot CLI"
echo "   2. Run: /skills list   (should show uxr-* skills)"
echo "   3. Create a project folder with research_config.yaml"
echo "   4. Say: \"Run the full analysis on my transcripts\""
echo ""
