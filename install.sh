#!/usr/bin/env bash
set -euo pipefail

REPO\_DIR="\$(cd "\$(dirname "\${BASH\_SOURCE[0]}")" && pwd)"
ZSHRC="\${HOME}/.zshrc"
FUNC\_DIR="\${HOME}/.local/share/ez\_terminal\_recorder"
FUNC\_SRC="\${FUNC\_DIR}/rec2md.zsh"
VAULT\_DIR="\${HOME}/obsidian/vault/term\_logs"

[[ -f "\${REPO\_DIR}/.env" ]] && source "\${REPO\_DIR}/.env"

deps=(script sed date mkdir)
missing=()
for dep in "\${deps[@]}"; do
  command -v "\$dep" >/dev/null 2>&1 || missing+=("\$dep")
done
if [[ \${#missing[@]} -gt 0 ]]; then
  echo "❌ Missing dependencies: \${missing[\*]}" >&2
  exit 1
fi

mkdir -p "\${EZ\_TERM\_LOG\_DIR:-\$VAULT\_DIR}"

mkdir -p "\$FUNC\_DIR"
cp "\${REPO\_DIR}/src/rec2md.zsh" "\$FUNC\_SRC"
chmod +x "\$FUNC\_SRC"

source\_line="source \"\${FUNC\_SRC}\""

if ! grep -Fxq "\$source\_line" "\$ZSHRC" 2>/dev/null; then
  {
    echo ""
    echo "# EZ Terminal Recorder – rec2md function"
    echo "\$source\_line"
    echo "export EZ\_TERM\_LOG\_DIR=\"\${EZ\_TERM\_LOG\_DIR:-\$VAULT\_DIR}\""
  } >> "\$ZSHRC"
  echo "✅ Added source line to \$ZSHRC"
else
  echo "ℹ️ rec2md already sourced in \$ZSHRC"
fi

echo "⚡ Run 'source \$ZSHRC' or open a new terminal to start using rec2md."
