FROM python:3.12 as ide

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID


# User setup
RUN groupadd -g "${USER_GID}" ${USERNAME} \
    && useradd --create-home --no-log-init --shell /bin/zsh -u "${USER_UID}" -g "${USER_GID}" ${USERNAME}

COPY ./.zshrc /tmp/.zshrc

RUN usermod -aG sudo ${USERNAME}
RUN apt-get update && apt-get install -y sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN echo "${USERNAME}:${USERNAME}" | chpasswd && adduser ${USERNAME} sudo

# Poetry setup
# Install required python packages
RUN rm -rf /poetry_specific_venv && mkdir -p /poetry_specific_venv
RUN rm -rf /poetry_specific_cache && mkdir -p /poetry_specific_cache
ENV PATH=/poetry_specific_venv/bin:$PATH VIRTUAL_ENV=/poetry_specific_venv
RUN chown -R $USERNAME /poetry_specific_venv && chgrp -R $USERNAME /poetry_specific_venv && chmod -R g+w /poetry_specific_venv
RUN chown -R $USERNAME /poetry_specific_cache && chgrp -R $USERNAME /poetry_specific_cache && chmod -R g+w /poetry_specific_cache

# COPY --from=mikefarah/yq:latest /usr/bin/yq /usr/bin/yq

# Setup poetry environment
USER vscode
RUN python -m venv /poetry_specific_venv
RUN /poetry_specific_venv/bin/pip install poetry pre-commit
RUN /poetry_specific_venv/bin/pip install pylint black mypy flake8 isort pytest

# RUN chown -R vsts /poetry_specific_venv && chgrp -R allusers /poetry_specific_venv && chmod -R g+w /poetry_specific_venv
# RUN find /poetry_specific_venv  -type d -exec chmod 2775 {} \; && find /poetry_specific_venv -type f -exec chmod ug+rw {} \;
# RUN chown -R vsts /poetry_specific_cache && chgrp -R allusers /poetry_specific_cache && chmod -R g+w /poetry_specific_cache
# RUN find /poetry_specific_cache  -type d -exec chmod 2775 {} \; && find /poetry_specific_cache -type f -exec chmod ug+rw {} \;

