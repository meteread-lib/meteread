# DSMR

Electricity and gas are both read from the same DSMR v5 P1 port (`/dev/ttyUSB0`). The `dsmr-parser` library handles telegram parsing.

## Gas sub-meter

Gas is delivered as a sub-meter on the MBus channel. `DSMRGasProcessor` identifies it by device type `3` (gas) inside `telegram.MBUS_DEVICES`.

## Output format

`DSMRElectricityProcessor` logs:

```
electricity sn=<id> t1=<kWh> t2=<kWh> now=<kW> returned=<kW>
```

`DSMRGasProcessor` logs:

```
gas sn=<id> reading=<value> <unit>
```

## Storage fields

When a storage backend is configured, processors write the following:

**Electricity** — measurement `electricity`, tag `sn`, fields `t1`, `t2`, `current`, `returned`

**Gas** — measurement `gas`, tag `sn`, fields `reading`
