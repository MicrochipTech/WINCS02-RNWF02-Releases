# RNWF02 Firmware Update Utility

A Python utility for downloading firmware to RNWF02 devices using AT commands over serial communication.

## What This Folder Contains

- `nvm-update.py`: main command-line tool
- `requirements.txt`: Python dependency list (`pyserial`)

## Features

- AT command-based firmware download for RNWF02 devices
- Automatic NVM sector erase before update
- Chunked firmware transfer with configurable chunk size
- Real-time progress tracking with transfer speed
- Firmware verification and activation
- Device reset with firmware version check
- Verbose debug mode for troubleshooting
- Color-coded output for better readability
- Cross-platform support (Windows/Linux)

## Requirements

- Python 3.6+
- pyserial library

## Installation

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

## How It Works

The firmware update process follows these steps:

1. **Communication Check**: Sends `AT` command to verify device is responding
2. **Get Firmware Version**: Retrieves current firmware version using `AT+GMR`
3. **Erase Sectors**: Executes `AT+NVMER` to erase NVM sectors (may take up to 30 seconds)
4. **Download Firmware**: Transfers firmware in chunks using `AT+NVMWR=<offset>,<length>,<hex_data>`
5. **Verify Firmware**: Validates the downloaded firmware with `AT+OTAVFY`
6. **Activate Firmware**: Executes `AT+OTAACT` to activate the downloaded firmware image
7. **Reset Device** (optional): Resets device with `AT+RST` and verifies new firmware version

## Usage

Basic syntax:
```powershell
python nvm-update.py -p <PORT> <FIRMWARE_FILE>
```

### Parameters

- `-p, --port`: Serial port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux) - **Required**
  - To list available ports with details, run: `python -m serial.tools.list_ports -v`
- `firmware`: Path to firmware binary file (e.g., `rnwf02_ota.bin`) - **Required**
- `-b, --baudrate`: Baud rate for serial communication (default: `230400`)
- `-c, --chunk-size`: Chunk size in bytes for firmware transfer (default: `128`)
  - **Note**: Chunk size must be a factor of 4096 and ≤ 1024 bytes, since a write cannot cross a sector boundary
- `-v, --verbose`: Enable verbose debug output showing AT commands and responses
- `--no-erase`: Skip erasing NVM sectors before firmware download
- `--no-activate`: Skip firmware verification and activation after download
- `--no-reset`: Skip device reset after firmware update
- `--read-verify`: Perform a read verification after writing each chunk

### Examples

**Windows:**
```powershell
# Basic usage with default settings
python nvm-update.py -p COM5 rnwf02_ota.bin

# Custom baud rate
python nvm-update.py -p COM5 -b 921600 rnwf02_ota.bin

# Larger chunk size for faster transfer
python nvm-update.py -p COM5 -c 256 rnwf02_ota.bin

# Verbose mode for debugging
python nvm-update.py -p COM5 -v rnwf02_ota.bin

# Skip device reset after update
python nvm-update.py -p COM5 --no-reset rnwf02_ota.bin

# Skip sector erase (useful for partial updates)
python nvm-update.py -p COM5 --no-erase rnwf02_ota.bin

# Skip activation (download only)
python nvm-update.py -p COM5 --no-activate rnwf02_ota.bin

# Download only without activation or reset
python nvm-update.py -p COM5 --no-activate --no-reset rnwf02_ota.bin
```

**Linux:**
```bash
# Basic usage
python nvm-update.py -p /dev/ttyUSB0 rnwf02_ota.bin

# With custom settings
python nvm-update.py -p /dev/ttyUSB0 -b 921600 -c 256 rnwf02_ota.bin
```

## Output Example

```
Starting firmware update...

Checking device communication...
✓ Device responding COM5 at 230400 bps

Getting firmware version...
✓ Firmware version: 3.2.0 1 74d4fbc2 [15:48:01 Jan 21 2026]

Erasing 240 sectors at offset 0...
✓ Sectors erased successfully

Downloading firmware from rnwf02_ota.bin (chunk size: 128 bytes)...
Chunk 1024/1024 (100%): 524288/524288 bytes
✓ Downloaded 524288 bytes in 45.2s (11.3 KB/s)

Verifying firmware...
✓ Firmware verified successfully

Activating firmware...
✓ Firmware activated successfully

Resetting device...
✓ Device reset command sent

Getting firmware version...
✓ Firmware version: 3.2.1 1 8a5c3fd9 [10:23:45 Jan 28 2026]

✓ Firmware update completed
```

## AT Commands Reference

The utility uses the following AT commands from the RNWF02 specification:

- `AT` - Check device communication
- `AT+GMR` - Get firmware version information
- `AT+NVMER=<offset>,<sectors>` - Erase NVM sectors before firmware update
- `AT+NVMRD=<offset>,<length>` - Read data from NVM for verification
- `AT+NVMWR=<offset>,<length>,<hex_data>` - Write firmware chunk to NVM
- `AT+OTAVFY` - Verify downloaded firmware image
- `AT+OTAACT` - Activate the downloaded firmware image
- `AT+RST` - Reset the device

## Troubleshooting

- **Connection Failed**: Verify COM port name and ensure device is connected
- **Permission Denied**: On Linux, you may need to add your user to the `dialout` group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
- **Timeout Errors**: Try using verbose mode (`-v`) to see detailed AT command exchanges
- **Wrong Baud Rate**: Verify device documentation for correct baud rate (default: 230400)
- **Slow Transfer**: Increase chunk size with `-c 256` or higher
- **Unexpected Response**: Use verbose mode to debug AT command responses
