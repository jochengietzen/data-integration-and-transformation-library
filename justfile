default:
    just --list

init_system_files:
    #!/bin/zsh
    set -euxo pipefail
    if [ -f /tmp/.gitconfig ]; then rm -rf /home/vscode/.gitconfig && cp /tmp/.gitconfig /home/vscode/.gitconfig; fi
    if [ -d /tmp/.ssh ]; then rm -rf /home/vscode/.ssh && cp -r /tmp/.ssh /home/vscode/.ssh && chmod 600 /home/vscode/.ssh/*; fi
    git config --global --add safe.directory '*'
    git config --global core.autocrlf input
    git config --global core.eol lf
    if [ -f /tmp/.zshrc ]; then cp /tmp/.zshrc /home/vscode/.zshrc; fi


init: init_system_files
    #!/bin/zsh
    set -euxo pipefail
    rm -rf .venv
    uv venv
    uv sync --all-groups --all-packages
    pre-commit install

check:
    #!/bin/sh
    uv run ruff check src/ tests/
    uv run pylint src/ tests/
    uv run mypy src/

ssh-fix:
    #!/bin/zsh
    set -euxo pipefail
    rm -rf /home/vscode/.ssh
    mkdir -p /home/vscode/.ssh
    cp /tmp/.ssh/* /home/vscode/.ssh
    chmod 600 /home/vscode/.ssh/*

unit-tests:
    #!/bin/bash
    shopt -s globstar
    export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=0 --cov-report term-missing:skip-covered --no-cov-on-fail ./tests/ ./plugins/**/tests/ ./examples/**/tests/
    # export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=90 --cov-report term-missing:skip-covered --no-cov-on-fail tests/ plugins/**/tests/ examples/**/tests/

docs:
    uv run zensical serve
