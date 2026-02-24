# Meteread

A Python utility for reading utility meter values (water, electricity, gas) with a composable reader/processor/storage
architecture.

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

This starts InfluxDB 3 on port `8181` and runs `meteread read raw` by default. Edit `compose.yaml` to change the meter
command or serial device.

## Architecture

Four composable layers wired together in `main.py`:

**Reader** (`reader/`) — implements Python's `Iterator` protocol via `AbstractReader`. `__next__` returns the raw data
for one reading. `DelayReader` decorates any reader with a sleep between reads. `DSMRv5SerialReader` reads from a DSMR
v5 smart meter over serial. `DSMRv5RawReader` parses a raw telegram string and yields it repeatedly — useful for testing
without hardware.

**Processor** (`processor/`) — a callable (`AbstractProcessor.__call__(data) -> None`) that receives each raw reading
and does something with it (print, store, etc.). `ChainProcessor` composes multiple processors so they all receive the
same data in sequence.

**Meter** (`meter/`) — `AbstractMeter.__call__` drives the loop: `while self.processor(next(self.reader)): pass`. Since
processors return `None` (falsy), this exits after one read. The outer `while True` in `main.py` calls `meter()`
repeatedly for continuous reading.

**Storage** (`storage/`) — an optional backend passed into processors.
`AbstractStorage.write(measurement, tags, fields, timestamp)` is the interface. `InfluxDBStorage` writes to InfluxDB 3.
`CsvStorage` appends rows to a CSV file.

## Configuration

Copy `.env.example` to `.env` and set:

| Variable       | Default                | Description         |
|----------------|------------------------|---------------------|
| `INFLUXDB_URL` | `http://influxdb:8181` | InfluxDB 3 base URL |

## Project Structure

```
meteread/
├── main.py
├── pyproject.toml
├── compose.yaml
├── Dockerfile
├── .env.example
├── mkdocs.yml
├── docs/
├── meter/
│   ├── AbstractMeter.py
│   └── GenericMeter.py
├── processor/
│   ├── AbstractProcessor.py
│   ├── ChainProcessor.py
│   ├── DSMRElectricityProcessor.py
│   ├── DSMRGasProcessor.py
│   ├── NoneProcessor.py
│   └── PassProcessor.py
├── reader/
│   ├── AbstractReader.py
│   ├── DelayReader.py
│   ├── DSMRv5RawReader.py
│   ├── DSMRv5SerialReader.py
│   ├── RandomReader.py
│   └── ZeroReader.py
├── storage/
│   ├── AbstractStorage.py
│   ├── CsvStorage.py
│   └── InfluxDBStorage.py
└── tests/
    ├── conftest.py
    ├── test_meters.py
    ├── test_processors.py
    ├── test_readers.py
    ├── test_storage.py
    ├── test_integration_csv.py
    └── test_integration_influxdb.py
```

## DSMR

Electricity and gas are both read from the same DSMR v5 P1 port. Gas is a sub-meter on the MBus channel —
`DSMRGasProcessor` finds it by device type (3 = gas) in `telegram.MBUS_DEVICES`.

`DSMRElectricityProcessor` prints:

```
electricity sn=<id> t1=<kWh> t2=<kWh> now=<kW> returned=<kW>
```

`DSMRGasProcessor` prints:

```
gas sn=<id> reading=<value> <unit>
```

## Docs

```bash
uv run zensical serve   # live preview at http://localhost:8000
uv run zensical build   # build static site to site/
```

## Testing

```bash
uv run pytest
```

## Extending

To add a new meter type: add a key to the `meters` dict in `main.py`, composing a reader and processor.

To add a new reader, subclass `AbstractReader` and implement `__next__`:

```python
from reader import AbstractReader


class MyReader(AbstractReader):
    def __next__(self):
        return 42.0
```

To add a new processor, subclass `AbstractProcessor` and implement `__call__`:

```python
from processor import AbstractProcessor


class MyProcessor(AbstractProcessor):
    def __call__(self, data) -> None:
        print(data)
```

To run multiple processors on the same reading, use `ChainProcessor`:

```python
from processor import ChainProcessor, DSMRElectricityProcessor, DSMRGasProcessor

ChainProcessor(DSMRElectricityProcessor(), DSMRGasProcessor())
```

To add a new storage backend, subclass `AbstractStorage` and implement `write`:

```python
from storage import AbstractStorage


class MyStorage(AbstractStorage):
    def write(self, measurement, tags, fields, timestamp=None):
        ...
```

Pass a storage instance to processors that support it:

```python
DSMRElectricityProcessor(storage=MyStorage())
```

## Dependencies

- **dsmr-parser** — DSMR v5 protocol parsing for Dutch smart meters
- **influxdb-client-3** — InfluxDB 3 write client
- **python-dotenv** — `.env` file loading
- **typer** — CLI framework
- Python 3.12+
