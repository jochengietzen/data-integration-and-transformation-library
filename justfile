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



create_sub_venvs:
    #!/bin/bash
    set -euo pipefail
    export venv_roots="{{justfile_directory()}}/examples {{justfile_directory()}}/plugins/engines {{justfile_directory()}}/plugins/runtime_systems"
    export cwd=$(pwd)
    for root in $venv_roots; do
        if [ ! -d "$root" ]; then
            echo "Skipping '$root': not a directory"
            continue
        fi
        for folder in "$root"/*/; do
            [ -d "$folder" ] || continue
            echo "Creating venv in: $folder"
            cd $folder
            rm -rf ".venv"
            # python -m venv ".venv"
            export UV_PROJECT_ENVIRONMENT="$folder/.venv"
            uv sync --all-groups --all-extras
        done
    done
    cd $cwd

init: init_system_files
    #!/bin/zsh
    set -euxo pipefail
    rm -rf .venv
    uv venv
    uv sync --all-groups
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
    export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=0 --cov-report term-missing:skip-covered --no-cov-on-fail tests/
    # export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=90 --cov-report term-missing:skip-covered --no-cov-on-fail tests/

docs:
    uv run zensical serve
