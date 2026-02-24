# Meteread

A Python utility for reading utility meter values (water, electricity, gas) with a composable reader/processor/storage architecture.

## Installation

```bash
git clone https://github.com/pashamray/meteread.git
cd meteread
cp .env.example .env
uv sync
```

## Usage

```bash
uv run python main.py read water
uv run python main.py read electricity
uv run python main.py read gas
uv run python main.py read electricity_and_gas
```

For testing without hardware, use the `raw` meter backed by a hardcoded DSMR v5 telegram:

```bash
uv run python main.py read raw
```

## Docker

Run the full stack (meteread + InfluxDB) with Docker Compose:

```bash
docker compose up -d
```

This starts InfluxDB 3 on port `8181` and runs `meteread read raw` by default. Edit `compose.yaml` to change the meter command or serial device.

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Default | Description |
|---|---|---|
| `INFLUXDB_URL` | `http://influxdb:8181` | InfluxDB 3 base URL |
