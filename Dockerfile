FROM selenium/standalone-chrome:98.0

USER root

WORKDIR /app

COPY . /app

RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends -y python3-pip; \
    rm -rf /var/lib/apt/lists/*; \
    pip3 install -r analyse/requirements.txt; \
    python3 --version; \
    pip3 --version

ENTRYPOINT ["python3", "analyse/app.py"]
