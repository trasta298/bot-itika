FROM python:3.12 as build

RUN apt-get update && apt-get install -y build-essential curl
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

COPY ./requirements.lock  .
RUN sed '/-e/d' requirements.lock > requirements.txt
RUN /root/.cargo/bin/uv venv /opt/venv && \
    /root/.cargo/bin/uv pip install --no-cache -r requirements.txt

FROM python:3.12-slim

WORKDIR /workspace

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/workspace"

VOLUME /data

COPY . .

CMD ["python", "src/bot_itika/main.py"]
