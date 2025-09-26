# installer for the Modbus ETH driver
# Copyright 2025 Florent Colinet

from weecfg.extension import ExtensionInstaller


def loader():
    return ModbusEthInstaller()


class ModbusEthInstaller(ExtensionInstaller):
    def __init__(self):
        super(ModbusEthInstaller, self).__init__(
            version="0.1",
            name='ModbusEth',
            description='ModbusEth driver for weewx.',
            author="Florent Colinet",
            author_email="23095517+FColinet@users.noreply.github.com",
            config={
                'Station': {
                    'station_type': 'ModbusEth'},
                'ModbusEth': {
                    'poll_interval': '10',
                    'path': '/var/tmp/datafile',
                    'driver': 'user.ModbusEth'}},
            files=[('bin/user', ['bin/user/modbus-eth.py'])]
        )
