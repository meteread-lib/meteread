# Use a Python image with uv pre-installed
FROM python:3.12-slim-trixie

LABEL authors="Pavlo Shamrai"
LABEL org.opencontainers.image.authors="Pavlo Shamrai"
LABEL org.opencontainers.image.description="A Python utility for reading utility meter values (water, electricity, gas) with a composable reader/processor/storage architecture."
LABEL org.opencontainers.image.source="https://github.com/pashamray/meteread"

COPY . /app

WORKDIR /app

RUN pip install --upgrade uv && uv sync --locked

ENTRYPOINT ["uv", "run", "python", "main.py"]