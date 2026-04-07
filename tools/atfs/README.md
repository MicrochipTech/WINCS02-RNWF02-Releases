# RNWF02 Filesystem Utility

CLI utility for managing RNWF02 files over UART using `AT+FS` and `AT+FSTSFR`.

## What This Folder Contains

- `atfs.py`: main command-line tool (recommended entry point)
- `atfs_tsfr.py`: low-level AT transport/helper layer used by `atfs.py`
- `requirements.txt`: Python dependency list (`pyserial`)

## Features

- Check module communication over serial
- List files in RNWF02 folders (`list`)
- Upload local files to device (`load`)
- Download files from device (`store`)
- Delete files on device (`delete`)
- Read filesystem info (`info`)

## Requirements

- Python 3.8+
- `pyserial>=3.5`

Install dependency:

```powershell
pip install -r requirements.txt
```

## Usage

```powershell
python atfs.py -p <PORT> [options] <command> [command args]
```

### Global Options

- `-p, --port` (required): serial port, for example `COM6` or `/dev/ttyUSB0`
- `-b, --baudrate`: serial baud rate (default: `230400`)
- `-v, --verbose`: print raw AT TX/RX trace

### Commands

- `info`
  - Show filesystem free space and free handle count

- `list <folder>`
  - List files in a folder

- `load <folder> <path> [name]`
  - Upload local file to device
  - If `name` is omitted, `fs.py` uses the local pathname stem

- `store <folder> <name> [path]`
  - Download file from device
  - If `path` is omitted, output filename defaults to `name`
  - If `path` is a directory, output filename defaults to `directory/name`
  - Overwrite protection is enabled by default; use `--force` to replace an existing local file

- `delete <folder> <name>`
  - Delete a device file

### Supported Folders

- `user`
- `cert`
- `key`
- `dh`
- `cfg`

## Filename Rules (Important)

Device filenames used by `load`, `store`, and `delete` must match this pattern:

- 1 to 32 characters
- Allowed: letters, digits, `_`, `-`
- Not allowed: dot (`.`) and other special characters

Good examples:

- `file1`
- `test`
- `autoexec`

Bad example:

- `file1.user`

## Examples

### Show filesystem status
```powershell
python atfs.py -p COM6 info
```
### Load with explicit device filename
```powershell
python atfs.py -p COM6 load user c:/certs/device.crt device_crt
```
### Load and auto-generate device filename from local file stem
```powershell
python atfs.py -p COM6 load cfg c:/rnwf/autoexec.txt
```
### Use custom baudrate and verbose trace output
```powershell
python atfs.py -p COM6 -b 921600 -v load user c:/data/blob.bin blob_bin
```
### List files in remote folder
```powershell
python atfs.py -p COM6 list cert
```
### Delete remote file
```powershell
python atfs.py -p COM6 -b 921600 delete cfg file1
```
### Store to explicit local file path
```powershell
python atfs.py -p COM6 store cfg autoexec c:/out/autoexec
```
### Store to directory (output file will use remote name)
```powershell
python atfs.py -p COM6 store cfg autoexec c:/out/
```
### Store with default local path (uses remote name in current directory)
```powershell
python atfs.py -p COM6 store cfg autoexec
```
### Allow overwrite of existing local output file
```powershell
python atfs.py -p COM6 store cfg autoexec c:/folder/cfg/ --force
```

### Linux equivalent examples
```bash
python atfs.py -p /dev/ttyUSB0 info
python atfs.py -p /dev/ttyUSB0 load user ./certs/device.crt device_crt
python atfs.py -p /dev/ttyUSB0 load cfg ./rnwf/autoexec.txt
python atfs.py -p /dev/ttyUSB0 -b 921600 -v load user ./data/blob.bin blob_bin
python atfs.py -p /dev/ttyUSB0 list cert
python atfs.py -p /dev/ttyUSB0 -b 921600 delete cfg file1
python atfs.py -p /dev/ttyUSB0 store cfg autoexec ./out/autoexec
python atfs.py -p /dev/ttyUSB0 store cfg autoexec ./out/
python atfs.py -p /dev/ttyUSB0 store cfg autoexec
python atfs.py -p /dev/ttyUSB0 store cfg autoexec ./folder/cfg/ --force
```

## Notes

- `atfs.py` starts by checking communication with `AT` before file commands.
- `atfs_tsfr.py` handles FS-TSFR protocol framing and payload encoding/decoding.

## Troubleshooting

- No response or timeout:
  - Verify port and baud rate
  - Confirm no other terminal/application has the COM port open
  - Try `-v` to inspect raw AT traffic

- Parse/response errors:
  - Check folder and filename values
  - Ensure device filename follows the allowed character rule

- Linux serial permission issues:
  - Add user to serial group (often `dialout`) and re-login
