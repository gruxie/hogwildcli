#!/usr/bin/env bash
# Hogwild UXR Installer for macOS/Linux
# Installs the MCP server and copies skills to Copilot CLI

set -e

echo "============================================"
echo " Hogwild UXR - Installer"
echo "============================================"
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "[ERROR] uv is not installed."
    echo "Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Installing MCP server package..."
uv pip install -e "$SCRIPT_DIR" --quiet
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
echo "[4/4] Verifying..."
echo "      Server registered (stdio transport — verified on first Copilot CLI use)."

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
