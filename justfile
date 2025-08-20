default:
    just --list

init:
    #!/bin/zsh
    set -euxo pipefail
    git config --global --add safe.directory '*'
    cp /tmp/.zshrc /home/vscode/.zshrc
    #rm -rf .venv
    #uv venv
    uv sync --all-groups
    pre-commit install
