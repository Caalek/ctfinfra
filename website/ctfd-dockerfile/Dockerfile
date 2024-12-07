FROM ctfd/ctfd:3.7.4

USER root

RUN apt-get update \
    && /opt/venv/bin/python -m pip install --upgrade pip \
    && apt-get install -y  pkg-config python3-dev default-libmysqlclient-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

USER ctfd

RUN pip install mysqlclient

COPY --chown=ctfd:ctfd files/ /opt/CTFd/CTFd/
COPY --chown=ctfd:ctfd files/plugins /opt/CTFd/CTFd/plugins

RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install -r $d/requirements.txt --no-cache-dir; \
        fi; \
    done;

