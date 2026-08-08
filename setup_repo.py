#!/usr/bin/env python3
"""
setup_repo.py - ez_terminal_recorder Repository Generator
"""
import os

FILES = {
    ".gitignore": """*.raw\n*.tmp\n*.cast\n.env\n.DS_Store\n*.swp\n*~\n.idea/\n.vscode/\n""",
    ".env.example": """EZ_TERM_LOG_DIR="${HOME}/obsidian/vault/term_logs"\n""",
    "LICENSE": """MIT License\nCopyright (c) 2026 ez_terminal_recorder\n""",
    "README.md": """# ez_terminal_recorder\n\nA lightweight Zsh utility for recording terminal sessions.\n""",
    "src/rec2md.zsh": """rec2md() {\n  echo "Recording session..."\n}\n""",
    "install.sh": """#!/usr/bin/env bash\necho "Installing..."\n""",
    "tests/run.sh": """#!/usr/bin/env bash\necho "Running tests..."\n"""
}

def main():
    for filepath, content in FILES.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        if filepath.endswith(".sh"):
            os.chmod(filepath, 0o755)
        print(f"Created: {filepath}")
    print("Repository structure generated successfully!")

if __name__ == "__main__":
    main()
