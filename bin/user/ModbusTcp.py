#!/usr/bin/env python
# Copyright 2025 Florent Colinet
# Distributed under the terms of the MIT License

"""Driver for collecting data from DIY weather station using modbus tcp
communication.

This driver requires the pymodbus python module.

pip install pymodbus
"""

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

import time

import weewx
import weewx.drivers
from weewx.wxformulas import calculate_rain

# --- Translation function stub (Standard practice for I18N) ---
# In a real setup, this would be linked to gettext, but we keep the
# base language (English) here for simplicity and compatibility with WeeWX.
def _(s):
    """Placeholder for translation function."""
    return s
# ----------------------------------------------------------------------


DRIVER_NAME = 'ModbusTcp'
DRIVER_DESC = 'Station with Modbus TCP gateway'
DRIVER_VERSION = '1.1.1'


try:
    # weewx4 logging
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)
    def logdbg(msg):
        log.debug(msg)
    def loginf(msg):
        log.info(msg)
    def logerr(msg):
        log.error(msg)
except ImportError:
    # old-style weewx logging
    import syslog
    def logmsg(level, msg):
        syslog.syslog(level, 'ModbusTcp: %s' % msg)
    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)
    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)
    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


def loader(config_dict, _):
    return ModbusTcpDriver(**config_dict[DRIVER_NAME])


def confeditor_loader():
    return ModbusTcpConfEditor()


class ModbusTcpConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[ModbusTcp]
    host = 192.168.1.100
    port = 502

    poll_interval = 10

    driver = user.ModbusTcp

    # ----------------------------------------------------
    # SENSOR DEFINITIONS (Stations)
    # ----------------------------------------------------

    #[[sensor_<name>]]
    #   slave_id = <id of device> # Unit ID Modbus, 1-247
    #   registry = <registry address> # Modbus Holding address or Input Register, often 0-based
    #   length = <number of registers to read> # typically 1
    #
    #   [[[<weewx packet name>]]] # ex: outTemp, windSpeed, radiation
    #       index = <registry index> # often 0-based
    #       scale = <multiplier value>
    #       data_type = <int16 (default) or int32> # Required for 32-bit values
    #
    # Example 1: 16-bit registers (Temperature, Humidity, ...)
    #
    #[[sensor_bme280]]
    #   slave_id = 1
    #   registry = 0
    #   length = 3
    #
    #   [[[outHumidity]]]
    #       index = 0
    #       scale = 0.1
    #
    #   [[[outTemp]]]
    #       index = 1
    #       scale = 0.1
    #
    #   [[[pressure]]]
    #       index = 2
    #       scale = 1
    #
    # Example 2: 32-bit register (Illumination/Radiation)
    # Note: length must be at least 2 for a 32-bit read (2x 16-bit words).
    #
    #[[sensor_light]]
    #   slave_id = 1
    #   registry = 2 
    #   length = 2
    #
    #   [[[radiation]]]
    #       index = 0
    #       scale = 0.001
    #       data_type = int32
"""

    def prompt_for_settings(self):
        # Use _() for strings displayed to the user
        print(_("Specify the host and port on which the station is connected, for"))
        print(_("example 192.168.1.100:502"))
        host = self._prompt(_('host'), ModbusTcp.DEFAULT_HOST)
        port = self._prompt(_('port'), ModbusTcp.DEFAULT_PORT)
        return {'host': host, 'port': port}


class ModbusTcpDriver(weewx.drivers.AbstractDevice):

    def __init__(self, **config_dict):
        loginf(_('driver version is %s') % DRIVER_VERSION)

        host = config_dict.get('host', ModbusTcp.DEFAULT_HOST)
        loginf(_("host is %s") % host)

        port = int(config_dict.get('port', ModbusTcp.DEFAULT_PORT))
        loginf(_("port is %s") % port)

        timeout = int(config_dict.get('timeout', ModbusTcp.DEFAULT_TIMEOUT))
        loginf(_("timeout is %s") % timeout)

        self.poll_interval = int(config_dict.get('poll_interval', 10))
        loginf(_("poll_interval is %s") % self.poll_interval)

        self.instruments = []

        # ----------------------------------------------------------------------
        # Reading sensors defined in weewx.conf
        # ----------------------------------------------------------------------
        for sensor_name, sensor_conf in config_dict.items():
            if sensor_name.startswith('sensor_'):
    
                if 'slave_id' not in sensor_conf:
                    logerr(_(f"Configuration error for {sensor_name}: 'slave_id' is mandatory and missing."))
                    continue

                try:
                    slave_id = int(sensor_conf.get('slave_id'))
                    registry_id = int(sensor_conf.get('registry', 1))
                    registry_length = int(sensor_conf.get('length', 1))
                except ValueError as e:
                    logerr(_(f"Configuration error for {sensor_name}: one of slave_id, registry, or length is not a valid number. Error: {e}"))
                    continue

                fields = dict()

                for field_name, field_conf in sensor_conf.items():
                    if isinstance(field_conf, dict):
                        try:
                            fields[field_name] = {
                                'index': int(field_conf.get('index', 0)),
                                'scale': float(field_conf.get('scale', 1.0)),
                                'data_type': field_conf.get('data_type', 'int16')
                            }
                        except ValueError as e:
                            logerr(_(f"Configuration error for field {field_name} in {sensor_name}: index or scale is not a valid number. Error: {e}"))
                            continue

                self.instruments.append({
                    'slave_id': slave_id,
                    'registry': registry_id,
                    'length': registry_length,
                    'fields': fields
                })

                loginf(_("Added sensor: %s:%s>%s for") % (slave_id, registry_id, registry_length))
                for field in fields:
                    loginf(_("    ==> %s") % field)

        self.station = ModbusTcp(host, port, timeout)

    @property
    def hardware_name(self):
        return DRIVER_DESC

    def closePort(self):
        self.station = None

    def _convert_value(self, values: list, field_conf: dict):
        index = field_conf['index']
        data_type = field_conf['data_type']

        if data_type == 'int16':
            return values[index]

        elif data_type == 'int32':
            if index + 1 >= len(values):
                raise IndexError("32-bit read requires two registers, but only one is available from index.")

            high_word = values[index]
            low_word = values[index + 1]
            
            int_value = (high_word << 16) + low_word
            return int_value

        else:
            logerr(_(f"Unsupported data type: {data_type}"))
            return None

    def genLoopPackets(self):
        while True:
            pkt = dict()
            pkt['dateTime'] = int(time.time() + 0.5)
            pkt['usUnits'] = weewx.METRIC

            for sensor in self.instruments:
                values = getattr(self.station, 'get_values')(sensor['slave_id'], sensor['registry'], sensor['length'])
                if values is not None:
                    for field_name, field_conf in sensor['fields'].items():
                        try:
                            raw_value = self._convert_value(values, field_conf)

                            if raw_value is not None:
                                value = raw_value * field_conf['scale']
                                pkt[field_name] = value
                                logdbg(_(f"Field {field_name} (Index {field_conf['index']}) = {value} (Raw: {raw_value})"))
                            # else: ignorer si la conversion a échoué (log fait dans _convert_value)

                        except IndexError:
                            logerr(_(f"Index {field_conf['index']} is out of bounds for the {len(values)} registers read."))

            yield pkt
            if self.poll_interval:
                time.sleep(self.poll_interval)


class ModbusTcp(ModbusTcpClient):
    DEFAULT_HOST = '192.168.1.100'
    DEFAULT_PORT = 502
    DEFAULT_TIMEOUT = 10 # seconds

    MAX_RECONNECT_DELAY = 60
    INITIAL_RECONNECT_DELAY = 5

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(host, port=port, timeout=timeout)

        self.last_connect_failure_ts = 0.0
        self.next_reconnect_attempt_ts = 0.0
        self.current_delay = self.INITIAL_RECONNECT_DELAY

    def __enter__(self):
        return self

    def __exit__(self, _):
        pass

    def get_values(self, slave_id: int, register: int, length: int):
        if time.time() < self.next_reconnect_attempt_ts:
            logdbg(_(f"Connection attempt skipped (backoff). Next try in {self.next_reconnect_attempt_ts - time.time():.1f}s."))
            return None

        try:
            if self.connect():
                if self.last_connect_failure_ts != 0.0:
                    loginf(_("Modbus reconnected successfully. Backoff reset."))

                self.last_connect_failure_ts = 0.0
                self.current_delay = self.INITIAL_RECONNECT_DELAY

                rr_read = self.read_holding_registers(address=register, count=length, device_id=slave_id)

                if rr_read.isError():
                    error_info = f"Exception Code: {rr_read.exception_code}" if hasattr(rr_read, 'exception_code') and rr_read.exception_code is not None else "Generic Error"
                    logerr(_(f"Register read error on {register} (ID {slave_id}): {error_info}. Raw response: {rr_read}"))
                    return None
                else:
                    return rr_read.registers
            else:
                logerr(_("Failed to connect to Modbus server."))
                self._apply_backoff()
                return None

        except ConnectionException:
            logerr(_("Connection error (network issue or server unavailable)."))
            self._apply_backoff()
            return None
        
        except Exception as e:
            logerr(_(f"Unexpected error during Modbus communication: {e}"))
            self._apply_backoff()
            return None

    def _apply_backoff(self):
        current_time = time.time()
        self.current_delay = min(self.current_delay * 2, self.MAX_RECONNECT_DELAY)
        self.next_reconnect_attempt_ts = current_time + self.current_delay
        logerr(_(f"Modbus connection failed. Next retry in {self.current_delay}s."))
        self.last_connect_failure_ts = current_time


if __name__ == '__main__':
    import optparse

    # Use _() for help strings
    usage = _("""%prog [options] [--debug] [--help]""")

    def main():
        syslog.openlog('wee_modbus_eth', syslog.LOG_PID | syslog.LOG_CONS)
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--version', dest='version', action='store_true',
                          help=_('display driver version'))
        parser.add_option('--debug', dest='debug', action='store_true',
                          help=_('display diagnostic information while running'))
        parser.add_option('--host', dest='host', metavar='HOST',
                          help=_('IP address to which the station is connected'),
                          default=ModbusTcp.DEFAULT_HOST)
        parser.add_option('--port', dest='port', metavar='PORT',
                          help=_('Port to which the station is connected'),
                          default=ModbusTcp.DEFAULT_PORT)
        parser.add_option('--timeout', dest='timeout', metavar='TIMEOUT',
                          help=_('modbus timeout, in seconds'), type=int,
                          default=ModbusTcp.DEFAULT_TIMEOUT)
        (options, _) = parser.parse_args()

        if options.version:
            print(_("ModbusTcp driver version %s") % DRIVER_VERSION)
            exit(1)

        if options.debug is not None:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

    main()
