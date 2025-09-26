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
weectl extension install https://github.com/FColinet/WeeWX-ModbusTCP-driver/archive/refs/heads/main.zip
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
    # WeeWX fields are extracted from the register block read.

    [[sensor_bme280]]
        # Modbus REQUEST parameters:
        slave_id = 10               # Modbus Slave Unit ID (1-247)
        registry = 0                # Starting register address (0-based)
        length = 3                  # Number of registers to read (e.g., 3)
        
        # Definition of WeeWX FIELDS extracted from the result:
        
        [[[outHumidity]]]
            index = 0               # Position of the register in the read block (0-based)
            scale = 0.1             # Multiplier for conversion (e.g., 255 -> 25.5)
            
        [[[outTemp]]]
            index = 1
            scale = 0.1
            
        [[[pressure]]]
            index = 2
            scale = 1
```

## License
This driver is distributed under the terms of the MIT License.

Copyright 2025 Florent Colinet
