ARG UV_VERSION=0.7.8


FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv


FROM mcr.microsoft.com/vscode/devcontainers/python:3.10-bullseye

ARG venv_path=/python_venv

    
    
COPY ./.zshrc /tmp/.zshrc
COPY --from=uv --chown=root: /uv /uvx /bin/

RUN apt-get update && apt-get install -y sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN pip install pipx
RUN pipx install --global rust-just pre-commit

