import logging
import os

import typer
from dotenv import load_dotenv

from meter import GenericMeter
from processor import PassProcessor, DSMRElectricityProcessor, DSMRGasProcessor, ChainProcessor
from reader import DelayReader, RandomReader, DSMRv5SerialReader, DSMRv5RawReader
from storage import InfluxDBStorage

logging.basicConfig(level=logging.INFO, format='[%(asctime)s - %(levelname)s]: %(message)s')
app = typer.Typer()

@app.command()
def main():
    typer.echo("Hello, I am Meteread!")

@app.command()
def read(name: str):
    storage = InfluxDBStorage(host=os.getenv('INFLUXDB_URL'), database='meteread')

    meters = {
        'water': GenericMeter(
            name='cold water',
            reader=DelayReader(
                reader=RandomReader(),
                delay=1.0
            ),
            processor=PassProcessor()
        ),
        'electricity': GenericMeter(
            name='electricity meter',
            reader=DSMRv5SerialReader(
                device='/dev/ttyUSB0'
            ),
            processor=DSMRElectricityProcessor()
        ),
        'gas': GenericMeter(
            name='gas meter',
            reader=DSMRv5SerialReader(
                device='/dev/ttyUSB0'
            ),
            processor=DSMRGasProcessor()
        ),
        'electricity_and_gas': GenericMeter(
            name='electricity and gas meter',
            reader=DSMRv5SerialReader(
                device='/dev/ttyUSB0'
            ),
            processor=ChainProcessor(
                DSMRElectricityProcessor(
                    storage=storage
                ),
                DSMRGasProcessor(
                    storage=storage
                ),
            )        ),
        'raw': GenericMeter(
            name='raw electricity and gas meter',
            reader=DelayReader(
                reader=DSMRv5RawReader(
                    raw=(
                        '/ISk5\\2MT382-1000\r\n'
                        '\r\n'
                        '5-3:0.2.8(50)\r\n'
                        '0-0:1.0.0(210101000000W)\r\n'
                        '0-0:96.1.1(4530303334303034363639353537343136)\r\n'
                        '1-0:1.8.1(001234.567*kWh)\r\n'
                        '1-0:1.8.2(002345.678*kWh)\r\n'
                        '1-0:2.8.1(000001.000*kWh)\r\n'
                        '1-0:2.8.2(000002.000*kWh)\r\n'
                        '0-0:96.14.0(0002)\r\n'
                        '1-0:1.7.0(01.500*kW)\r\n'
                        '1-0:2.7.0(00.000*kW)\r\n'
                        '0-0:96.7.21(00000)\r\n'
                        '0-0:96.7.9(00000)\r\n'
                        '1-0:32.32.0(00000)\r\n'
                        '1-0:52.32.0(00000)\r\n'
                        '1-0:72.32.0(00000)\r\n'
                        '1-0:32.36.0(00000)\r\n'
                        '1-0:52.36.0(00000)\r\n'
                        '1-0:72.36.0(00000)\r\n'
                        '1-0:32.7.0(230.1*V)\r\n'
                        '1-0:52.7.0(230.2*V)\r\n'
                        '1-0:72.7.0(230.0*V)\r\n'
                        '1-0:31.7.0(001*A)\r\n'
                        '1-0:51.7.0(002*A)\r\n'
                        '1-0:71.7.0(003*A)\r\n'
                        '1-0:21.7.0(00.500*kW)\r\n'
                        '1-0:41.7.0(00.500*kW)\r\n'
                        '1-0:61.7.0(00.500*kW)\r\n'
                        '1-0:22.7.0(00.000*kW)\r\n'
                        '1-0:42.7.0(00.000*kW)\r\n'
                        '1-0:62.7.0(00.000*kW)\r\n'
                        '0-1:24.1.0(003)\r\n'
                        '0-1:96.1.0(4730303233353631323930333635383137)\r\n'
                        '0-1:24.2.1(210101120000W)(01234.567*m3)\r\n'
                        '!0000\r\n'
                    )
                )
            ),
            processor=ChainProcessor(
                DSMRElectricityProcessor(
                    storage=storage
                ),
                DSMRGasProcessor(
                    storage=storage
                ),
            )
        ),
    }
    meter = meters.get(name)

    while True:
        meter()


@app.command()
def config():
    raise NotImplementedError


if __name__ == "__main__":
    load_dotenv()
    app()
