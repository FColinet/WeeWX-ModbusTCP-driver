# installer for the Modbus TCP driver
# Copyright 2025 Florent Colinet

from weecfg.extension import ExtensionInstaller


def loader():
    return ModbusTcpInstaller()


class ModbusTcpInstaller(ExtensionInstaller):
    def __init__(self):
        super(ModbusTcpInstaller, self).__init__(
            version="1.1",
            name='ModbusTcp',
            description='ModbusTcp driver for weewx.',
            author="Florent Colinet",
            author_email="23095517+FColinet@users.noreply.github.com",
            config={
                'Station': {
                    'station_type': 'Station with Modbus TCP gateway'
                },
                'ModbusTcp': {
                    'host': '192.168.1.100',
                    'port': 502,
                    'poll_interval': '10',
                    'driver': 'user.ModbusTcp'
                }
            },
            files=[('bin/user', ['bin/user/ModbusTcp.py'])]
        )
