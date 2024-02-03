FROM python:3.11

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

COPY /requirements.txt /src/requirements.txt
RUN apt update && apt-get install -y gnupg2 apt-transport-https \
    && curl https://baltocdn.com/helm/signing.asc | gpg --dearmor > /usr/share/keyrings/helm.gpg \
    && chmod 644 /usr/share/keyrings/helm.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" > /etc/apt/sources.list.d/helm-stable-debian.list \
    && apt-get update \
    && apt-get install helm -y \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && addgroup --gid 500 --system app \
    && adduser --system --home /app/ --uid 500 --gid 500 app \
    && pip install -U pip watchdog argh \
    && pip install -r /src/requirements.txt \
    && rm -rf /root/.cache/* var/lib/apt/lists/* \
    # Required for updating the libs
    && ldconfig

COPY . /src

RUN pip install -e /src

CMD python -m k8s_agent