# Extending

## Add a new meter type

Add a key to the `meters` dict in `main.py`, composing a reader and processor:

```python
'my_meter': GenericMeter(
    name='my meter',
    reader=DelayReader(reader=MyReader(), delay=5.0),
    processor=MyProcessor()
),
```

## Add a reader

Subclass `AbstractReader` and implement `__next__`:

```python
from reader import AbstractReader

class MyReader(AbstractReader):
    def __next__(self):
        return 42.0
```

## Add a processor

Subclass `AbstractProcessor` and implement `__call__`:

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

## Add a storage backend

Subclass `AbstractStorage` and implement `write`:

```python
from storage import AbstractStorage

class MyStorage(AbstractStorage):
    def write(self, measurement, tags, fields, timestamp=None):
        ...
```

Pass it to any processor that accepts a `storage` argument:

```python
DSMRElectricityProcessor(storage=MyStorage())
```
