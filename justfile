default:
    just --list

init:
    #!/bin/zsh
    set -euxo pipefail
    git config --global --add safe.directory '*'
    git config --global core.autocrlf input
    git config --global core.eol lf
    if [ -f /tmp/.zshrc ]; then cp /tmp/.zshrc /home/vscode/.zshrc; fi
    rm -rf .venv
    uv venv
    uv sync --all-groups
    pre-commit install
