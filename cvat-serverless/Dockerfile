FROM ubuntu:20.04

ARG http_proxy
ARG https_proxy

ARG TZ="Etc/UTC"

ENV TERM=xterm \
    http_proxy=${http_proxy}   \
    https_proxy=${https_proxy} \
    no_proxy=${no_proxy} \
    socks_proxy=${socks_proxy} \
    LANG='C.UTF-8'  \
    LC_ALL='C.UTF-8' \
    TZ=${TZ}
ARG USER="django"

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends install -yq \
        pkg-config \
        python3-dev \
        python3-pip \
        python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Add a non-root user
ENV USER=${USER}
ENV HOME /home/${USER}
RUN adduser --shell /bin/bash --disabled-password --gecos "" ${USER}

RUN python3 -m pip install --no-cache-dir -U pip==21.0.1 setuptools==53.0.0 wheel==0.36.2
RUN pip install django==3.2.6 djangorestframework==3.12.4 pyyaml==5.4.1 numpy==1.19.3 \
       Pillow==8.3.1 boto3==1.18.32 scipy==1.7.1

# RUN all commands below as 'django' user
USER ${USER}
WORKDIR ${HOME}

COPY --chown=${USER} manage.py ${HOME}/manage.py
COPY serverless/ ${HOME}/serverless
COPY functions/ ${HOME}/functions
COPY data.yaml ${HOME}/data.yaml

RUN python3 ${HOME}/manage.py migrate
RUN python3 ${HOME}/manage.py loaddata ${HOME}/data.yaml

EXPOSE 8070
CMD python3 ${HOME}/manage.py runserver 0.0.0.0:8070