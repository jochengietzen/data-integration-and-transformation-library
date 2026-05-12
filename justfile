default:
    just --list

init_system_files:
    #!/bin/zsh
    set -euxo pipefail
    if [ "$CI" != true ]; then
        if [ -f /tmp/.gitconfig ]; then rm -rf /home/vscode/.gitconfig && cp /tmp/.gitconfig /home/vscode/.gitconfig; fi
        if [ -d /tmp/.ssh ]; then rm -rf /home/vscode/.ssh && cp -r /tmp/.ssh /home/vscode/.ssh && chmod 600 /home/vscode/.ssh/*; fi
        git config --global --add safe.directory '*'
        git config --global core.autocrlf input
        git config --global core.eol lf
        if [ -f /tmp/.zshrc ]; then cp /tmp/.zshrc /home/vscode/.zshrc; fi
    fi


venv-roots := "/workspace/examples /workspace/plugins/engine_conversions /workspace/plugins/engines /workspace/plugins/runtime_systems"

create_sub_venvs:
    #!/bin/zsh
    set -euo pipefail
    for root in {{ venv-roots }}; do
        if [ ! -d "$root" ]; then
            echo "Skipping '$root': not a directory"
            continue
        fi
        for folder in "$root"/*/; do
            [ -d "$folder" ] || continue
            echo "Creating venv in: $folder"
            rm -rf "$folder/.venv"
            python -m venv "$folder/.venv"
        done
    done

init: init_system_files
    #!/bin/zsh
    set -euxo pipefail
    if [ "$CI" != true ]; then
        rm -rf .venv
        uv venv
        uv sync --all-groups
        pre-commit install
    fi

check:
    #!/bin/zsh
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
    export TZ="UTC"; uv run pytest --cov=ditl --cov-fail-under=90 --cov-report term-missing:skip-covered --no-cov-on-fail tests/