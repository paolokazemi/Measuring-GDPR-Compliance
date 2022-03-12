FROM selenium/standalone-chrome:98.0

USER root

WORKDIR /app

COPY analyse/requirements.txt /requirements.txt

RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends -y python3-pip; \
    rm -rf /var/lib/apt/lists/*; \
    pip3 install -r /requirements.txt; \
    python3 --version; \
    pip3 --version
