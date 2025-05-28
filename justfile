default:
    just --list

init:
    #!/bin/zsh
    set -euxo pipefail
    cp /tmp/.zshrc /home/vscode/.zshrc 
    uv venv
    uv sync --all-groups
    pre-commit install
