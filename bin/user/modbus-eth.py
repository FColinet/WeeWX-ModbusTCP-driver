#!/usr/bin/env python
# Copyright 2025 Florent Colinet
# Distributed under the terms of the MIT License

"""Driver for collecting data from DIY weather station using modbus tcp
communication.

This driver requires the pyModbusTCP python module.

pip install pyModbusTCP
"""

from pyModbusTCP.client import ModbusClient
import struct
import syslog
import time

import weewx
import weewx.drivers
from weewx.wxformulas import calculate_rain


DRIVER_NAME = 'ModbusEth'
DRIVER_VERSION = '0.1'


def logmsg(dst, msg):
    syslog.syslog(dst, 'ModbusEth: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logcrt(msg):
    logmsg(syslog.LOG_CRIT, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


def loader(config_dict, _):
    return ModbusEthDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return ModbusEthConfEditor()


class ModbusEthConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[ModbusEth]
    # Options générales pour la passerelle Modbus<->Eth (ex: NB114)
    host = 192.168.1.100  # <--- IP
    port = 502            # <--- Port

    # How often to poll the device, in seconds
    poll_interval = 10

    # ----------------------------------------------------
    # DÉFINITION DE VOS CAPTEURS (Stations)
    # ----------------------------------------------------

    sensors = [{
        'field': 'outTemp', # <--- WeeWX field name
        'slave_id': 1,
        'registry': 40001,
        'scale': 10
    }, {
        'field': 'outHumidity',
        'slave_id': 1,
        'registry': 40002,
        'scale': 1
    }, {
        'field': 'windSpeed',
        'slave_id': 2,
        'registry': 40010,
        'scale': 100
    }, ...]
"""

    def prompt_for_settings(self):
        print("Specify the host and port on which the station is connected, for")
        print("example 192.168.1.100:502")
        host = self._prompt('host', '192.168.1.100')
        port = self._prompt('port', 502)
        return {'host': host, 'port': port}


class ModbusEthDriver(weewx.drivers.AbstractDevice):

    def __init__(self, **stn_dict):
        loginf('driver version is %s' % DRIVER_VERSION)

        host = stn_dict.get('host', ModbusEth.DEFAULT_HOST)
        loginf("host is %s" % host)
        port = stn_dict.get('port', ModbusEth.DEFAULT_PORT)
        loginf("port is %s" % port)

        self.poll_interval = int(stn_dict.get('poll_interval', 10))
        loginf("poll interval is %s" % self.poll_interval)

        self.station = ModbusEth(host, port)

    def closePort(self):
        self.station = None


class ModbusEth(ModbusClient):
    DEFAULT_HOST = '192.168.1.100'
    DEFAULT_PORT = 502
    DEFAULT_BAUD_RATE = 9600
    DEFAULT_TIMEOUT = 6.0 # seconds

    def __init__(self, host, port):
        ModbusClient(host, port, unit_id=1, auto_open=True)

    def __enter__(self):
        return self

    def __exit__(self, _, value, traceback):
        pass


if __name__ == '__main__':
    import optparse

    usage = """%prog [options] [--debug] [--help]"""

    def main():
        syslog.openlog('wee_modbus_eth', syslog.LOG_PID | syslog.LOG_CONS)
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--version', dest='version', action='store_true',
                          help='display driver version')
        parser.add_option('--debug', dest='debug', action='store_true',
                          help='display diagnostic information while running')
        parser.add_option('--host', dest='host', metavar='HOST',
                          help='IP address to which the station is connected',
                          default=ModbusEth.DEFAULT_PORT)
        parser.add_option('--port', dest='port', metavar='PORT',
                          help='Port to which the station is connected',
                          default=ModbusEth.DEFAULT_PORT)
        parser.add_option('--baud-rate', dest='baud_rate', metavar='BAUD_RATE',
                          help='modbus slave baud rate', type=int,
                          default=ModbusEth.DEFAULT_BAUD_RATE)
        parser.add_option('--timeout', dest='timeout', metavar='TIMEOUT',
                          help='modbus timeout, in seconds', type=int,
                          default=ModbusEth.DEFAULT_TIMEOUT)
        parser.add_option('--get-time', dest='gettime', action='store_true',
                          help='get station time')
        parser.add_option('--set-time', dest='settime', action='store_true',
                          help='set station time to computer time')
        (options, _) = parser.parse_args()

        if options.version:
            print("ModbusEth driver version %s" % DRIVER_VERSION)
            exit(1)

        if options.debug is not None:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

    main()