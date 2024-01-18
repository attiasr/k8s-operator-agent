FROM python:3.11

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

COPY /requirements.txt /src/requirements.txt
RUN addgroup --gid 500 --system app \
    && adduser --system --home /app/ --uid 500 --gid 500 app \
    && pip install -U pip watchdog argh \
    && pip install -r /src/requirements.txt \
    && rm -rf /root/.cache/* \
    # Required for updating the libs
    && ldconfig

COPY . /src

RUN pip install /src

CMD python -m k8s_agent