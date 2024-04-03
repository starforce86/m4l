# syntax=docker/dockerfile:1.5

ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS base

COPY <<EOF /etc/apt/apt.conf.d/00-docker
APT::Install-Suggests "0";
APT::Install-Recommends "0";
EOF

RUN --mount=type=cache,target=/var/cache/apt echo "Installing base dependencies..." \
    && DEBIAN_FRONTEND=noninteractive apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        cron \
        gdal-bin \
        libfreetype6 \
        libjpeg8 \
        libmagic-dev \
        libmemcached-dev \
        locales \
        python3 \
        python3-pip \
    && DEBIAN_FRONTEND=noninteractive apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

###############################################################################

FROM base AS base-with-user

ARG USER_UID=1000
ARG USER_GID=1000
ARG USER_DIRS="/app /home/tendenci /var/log/tendenci"

RUN echo "Creating non-root user..." \
    && groupadd --gid ${USER_GID} tendenci \
    && useradd --shell /bin/bash --gid ${USER_GID} --uid ${USER_UID} tendenci \
    && mkdir --parents ${USER_DIRS} \
    && chown --recursive ${USER_UID}:${USER_GID} ${USER_DIRS} \
    && chmod --recursive -x+X,g+rw,o-rwx /var/log/tendenci

ENV APP_LOG_FILE=/var/log/tendenci/app.log
ENV DEBUG_LOG_FILE=/var/log/tendenci/debug.log

###############################################################################

FROM base-with-user AS deps-common

ARG USER_UID=1000
ARG USER_GID=1000

RUN --mount=type=cache,target=/var/cache/apt echo "Installing build dependencies..." \
    && DEBIAN_FRONTEND=noninteractive apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        libevent-dev \
        libfreetype6-dev \
        libgdal-dev \
        libjpeg-dev \
        libpq-dev \
        python3-dev \
    && DEBIAN_FRONTEND=noninteractive apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=${USER_UID}:${USER_GID} ./m4l-tendenci/requirements.txt /app/requirements-tendenci.txt
COPY --chown=${USER_UID}:${USER_GID} ./momsforliberty/requirements/common.txt /app/requirements-common.txt

USER tendenci

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN --mount=type=cache,target=/home/tendenci/.cache/pip,uid=${USER_UID},gid=${USER_GID} \
    pip3 install --user --upgrade --no-warn-script-location \
        -r /app/requirements-tendenci.txt \
        -r /app/requirements-common.txt

###############################################################################

FROM deps-common AS deps-development

ARG USER_UID=1000
ARG USER_GID=1000

COPY --chown=${USER_UID}:${USER_GID} ./momsforliberty/requirements/dev_only.txt /app/requirements-dev_only.txt

USER tendenci

RUN --mount=type=cache,target=/home/tendenci/.cache/pip,uid=${USER_UID},gid=${USER_GID} \
    pip3 install --user --upgrade --no-warn-script-location \
        -r /app/requirements-dev_only.txt

###############################################################################

FROM deps-common AS deps-production

ARG USER_UID=1000
ARG USER_GID=1000

COPY --chown=${USER_UID}:${USER_GID} ./momsforliberty/requirements/prod_only.txt /app/requirements-prod_only.txt

USER tendenci

RUN --mount=type=cache,target=/home/tendenci/.cache/pip,uid=${USER_UID},gid=${USER_GID} \
    pip3 install --user --upgrade --no-warn-script-location \
        -r /app/requirements-prod_only.txt

###############################################################################

FROM base-with-user AS development

ARG USER_UID=1000
ARG USER_GID=1000

USER tendenci

ENV PATH="$PATH:/home/tendenci/.local/bin"
ENV TENDENCI_PROJECT_ROOT=/app/momsforliberty

WORKDIR ${TENDENCI_PROJECT_ROOT}

COPY --chown=${USER_UID}:${USER_GID} --from=deps-development /home/tendenci/.local /home/tendenci/.local

COPY --chown=${USER_UID}:${USER_GID} <<'EOF' /usr/local/bin/docker-entrypoint.sh
#!/bin/bash
set -Eeuo pipefail
pip3 show tendenci &>/dev/null || pip3 install --user --upgrade -r requirements/dev.txt
exec "$@"
EOF
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT [ "docker-entrypoint.sh" ]

EXPOSE 8000

CMD ["python3", "./manage.py", "runserver", "0.0.0.0:8000"]

###############################################################################

FROM base-with-user AS production

ARG USER_UID=1000
ARG USER_GID=1000

USER tendenci

ENV PATH="$PATH:/home/tendenci/.local/bin"
ENV TENDENCI_SOURCE_ROOT=/app/m4l-tendenci
ENV TENDENCI_PROJECT_ROOT=/app/momsforliberty

WORKDIR ${TENDENCI_PROJECT_ROOT}

COPY --chown=${USER_UID}:${USER_GID} ./m4l-tendenci   ${TENDENCI_SOURCE_ROOT}
COPY --chown=${USER_UID}:${USER_GID} ./momsforliberty ${TENDENCI_PROJECT_ROOT}

COPY --chown=${USER_UID}:${USER_GID} --from=deps-production /home/tendenci/.local /home/tendenci/.local

RUN --mount=type=cache,target=/home/tendenci/.cache/pip,uid=${USER_UID},gid=${USER_GID} \
    pip3 install --user --upgrade -r requirements/prod.txt

#RUN <<EOF
#(
#    crontab -l 2>/dev/null || echo -n ""
#    echo "30 2 * * * cd ${TENDENCI_PROJECT_ROOT} && python3 manage.py run_nightly_commands"
#    echo "30 2 * * * cd ${TENDENCI_PROJECT_ROOT} && python3 manage.py process_unindexed"
#) | crontab -
#EOF

EXPOSE 8000

CMD ["gunicorn", "conf.wsgi:application", "--preload", "--bind", "0.0.0.0:8000"]
