# Release Notes - WeeWX ModbusTcp Driver

## Version 1.1 - Feature Release: 32-bit Data Support

**Release Date:** October 3, 2025

This minor release introduces a crucial feature for compatibility with sensors that report high-resolution or accumulated values across two Modbus registers.

### ✨ New Feature

#### 32-bit Value Support (`int32`)

* **New Addition:** The configuration parameter **`data_type = int32`** has been added to the field definitions in `weewx.conf`.
* **Functionality:** The driver can now read two consecutive 16-bit registers and assemble them into a single 32-bit integer, primarily used for sensors such as illumination (`radiation`).
* **Robustness:** Includes specific error handling to detect and log if the configured Modbus read length is insufficient for the requested 32-bit type.

### 🐛 Bug Fixes and Minor Improvements

* Updated the `default_stanza` documentation to include a clear example for using `data_type = int32`.

---

## Version 1.0 - Initial Stable Release

This major release provides a stable, robust platform for reading Modbus TCP data into WeeWX.

### 🚀 Key Features

#### Enhanced Connection Resilience

* **Exponential Backoff:** Implemented an exponential backoff strategy for all connection failures. The driver now automatically increases the delay between reconnection attempts (up to 60s max) to prevent network flooding and reduce system load during outages.
* **Advanced Diagnostics:** Modbus protocol errors now log the **specific Modbus exception code**, which simplifies the troubleshooting of configuration issues (e.g., `ILLEGAL DATA ADDRESS`).

#### Configuration Stability

* **Input Validation:** Strict validation of all mandatory configuration parameters (`slave_id`, `registry`, `length`, `index`, `scale`) during driver startup.

---
*License: Distributed under the MIT License.*