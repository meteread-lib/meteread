# Architecture

Four composable layers are wired together in `main.py`:

## Reader

`reader/` — implements Python's `Iterator` protocol via `AbstractReader`. `__next__` returns a parsed DSMR telegram. Available readers:

- **`DSMRv5SerialReader`** — reads from a DSMR v5 P1 port over serial
- **`DSMRv5RawReader`** — parses a raw telegram string and yields it repeatedly (useful for testing without hardware)
- **`DelayReader`** — wraps any reader and sleeps between reads
- **`RandomReader`** — yields random floats (used for the water meter placeholder)

## Processor

`processor/` — a callable (`AbstractProcessor.__call__(data) -> None`) that receives each telegram and does something with it. Available processors:

- **`DSMRElectricityProcessor`** — logs electricity readings and optionally writes to storage
- **`DSMRGasProcessor`** — logs gas readings and optionally writes to storage
- **`ChainProcessor`** — fans one telegram out to multiple processors in sequence
- **`PassProcessor`** — no-op, passes data through

All implementations return `None`.

## Storage

`storage/` — optional persistence backend passed into processors. The interface:

```python
AbstractStorage.write(measurement: str, tags: dict, fields: dict, timestamp: datetime | None = None) -> None
```

Available backends:

- **`InfluxDBStorage`** — writes to InfluxDB 3
- **`CsvStorage`** — appends rows to a CSV file

## Meter

`meter/` — `AbstractMeter.__call__` drives the read loop:

```python
while self.processor(next(self.reader)):
    pass
```

Since processors return `None` (falsy), this exits after one read. The outer `while True` in `main.py` calls `meter()` repeatedly for continuous reading.

## Composition example

The `raw` meter in `main.py` shows how all four layers compose together:

```python
GenericMeter(
    name='raw electricity and gas meter',
    reader=DelayReader(
        reader=DSMRv5RawReader(raw=...),
    ),
    processor=ChainProcessor(
        DSMRElectricityProcessor(storage=storage),
        DSMRGasProcessor(storage=storage),
    )
)
```
