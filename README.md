# WeeWX ModbusTcp Driver
WeeWX driver for collecting weather data from Modbus TCP-enabled weather stations or DIY sensor setups.

This driver is optimized for multi-register reads (grouped reading) to minimize network requests and polling time.

## Prerequisites
This driver requires the pymodbus Python module.

```Bash
pip install pymodbus
```

## Installation
Place the ModbusTcp.py file (your driver) into the bin/user/ directory of your WeeWX installation.

Update your weewx.conf configuration file.

Or launch this command

```bash
weectl extension install https://github.com/FColinet/WeeWX-ModbusTCP-driver/archive/refs/tags/1.1.zip
```

## WeeWX Configuration
In your weewx.conf file, add or modify the following stanza:

```TOML
[ModbusTcp]
    host = 192.168.1.100    # IP address of the Modbus device
    port = 502              # Standard Modbus TCP port
    timeout = 10            # Connection timeout (seconds)
    poll_interval = 10      # Polling interval between reads (seconds)
    
    driver = user.ModbusTcp

    # ------------------------------------------------------------------
    # SENSOR DEFINITIONS (Reading Groups)
    # ------------------------------------------------------------------
    
    # Each [[sensor_<name>]] section defines a SINGLE Modbus request.
    #
    # [[[<weewx packet name>]]] now supports 'data_type' (int16 or int32).

    # Example 1: Standard 16-bit registers (Temperature, Humidity)
    [[sensor_temp]]
        slave_id = 1
        registry = 0
        length = 3

        [[[outTemp]]]
            index = 1
            scale = 0.1
            # data_type defaults to int16

        ...
    
    # Example 2: 32-bit register (Illumination/Radiation)
    # Note: 'length' must be at least 2 for a 32-bit value.
    [[sensor_light]]
        slave_id = 1
        registry = 2 
        length = 2
        
        [[[radiation]]]
            index = 0               # Starts at the first register of the 32-bit value
            scale = 0.001           # E.g., for conversion (849011 -> 849.011)
            data_type = int32       # Tells the driver to combine index 0 and 1
```

## License
This driver is distributed under the terms of the MIT License.

Copyright 2025 Florent Colinet
