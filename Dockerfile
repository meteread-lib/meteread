# Use a Python image with uv pre-installed
FROM python:3.12-slim-trixie

LABEL authors="ps"

COPY . /app

WORKDIR /app

RUN pip install --upgrade uv && uv sync --locked

ENTRYPOINT ["uv", "run", "python", "main.py"]