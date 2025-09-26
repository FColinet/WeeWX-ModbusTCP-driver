# Release Notes - WeeWX ModbusTcp Driver

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