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
    export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=0 --cov-report term-missing:skip-covered --no-cov-on-fail tests/
    # export TZ="UTC"; uv run pytest --cov=eltstar --cov-fail-under=90 --cov-report term-missing:skip-covered --no-cov-on-fail tests/

run_all_tests:
    #!/bin/zsh
    #aigen_start
    set -uxo pipefail
    failed=()
    for f in $(find examples plugins -mindepth 2 -maxdepth 4 -name pyproject.toml); do
        dir=$(dirname "$f")
        [ -d "$dir/tests" ] || continue
        name=$(grep -m1 '^name' "$f" | sed -E 's/name\s*=\s*"(.*)"/\1/')
        echo "== $name =="
        uv run --package "$name" pytest "$dir/tests" || failed+=("$name")
    done
    if [ ${#failed[@]} -gt 0 ]; then
        echo "Failed packages: ${failed[@]}"
        exit 1
    fi
    #aigen_end

docs:
    uv run zensical serve
