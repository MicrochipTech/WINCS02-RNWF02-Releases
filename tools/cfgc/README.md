# cfgc — Configuration Command Compiler

A Python utility for compiling, encoding, and decoding WINCS02/RNWF02 configuration commands.

Configuration files produced by this tool can be included in a flash file system image built with the [flfs](../flfs/) tool, allowing the device to automatically apply settings at boot.

## What This Folder Contains

- `cfgc.py`: main command-line tool
- `requirements.txt`: Python dependency list (`pyclibrary`)
- `examples/test_vectors.at`: sample AT command input
- `examples/test_vectors.json`: sample JSON representation

## Modes of Operation

| Mode | Description |
|------|-------------|
| **Compile** (`-c`) | Parse AT commands from a text file into a JSON representation |
| **Encode** (`-e`) | Encode a JSON representation into binary configuration format |
| **Decode** (`-d`) | Decode a binary configuration file back into JSON |

Compile and encode can be combined (`-c -e`) to go directly from AT commands to binary.

## Prerequisites

- Python 3.6+
- [pyclibrary](https://pypi.org/project/pyclibrary/)

```
pip install -r requirements.txt
```

## Usage

```
cfgc.py [-H <header>] -i <infile> [-o <outfile>] [-c] -e
cfgc.py [-H <header>] -i <infile> [-o <outfile>] -d
cfgc.py -h
```

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help information |
| `-H <header>`, `--header=<header>` | Path to the interface header file (defaults to `WINCS02/driver/src/include/microchip_wincs02_intf.h` in this repo) |
| `-i <infile>`, `--in=<infile>` | Input file |
| `-o <outfile>`, `--out=<outfile>` | Output file (stdout if omitted) |
| `-c`, `--compile` | Compile AT commands to JSON |
| `-e`, `--encode` | Encode JSON to binary |
| `-d`, `--decode` | Decode binary to JSON |

## Examples

**Compile AT commands to JSON:**
```
python cfgc.py -c -i commands.at -o commands.json
```

**Compile and encode AT commands directly to binary:**
```
python cfgc.py -c -e -i commands.at -o config.bin
```

**Encode a JSON file to binary:**
```
python cfgc.py -e -i commands.json -o config.bin
```

**Decode a binary configuration file:**
```
python cfgc.py -d -i config.bin -o config.json
```

**Use a specific interface header:**
```
python cfgc.py -H path/to/microchip_wincs02_intf.h -c -e -i commands.at -o config.bin
```

## AT Command Format

Input AT command files use the standard AT command syntax with optional inline comments:

```
AT+WSTA=1,"MySSID","MyPassword",6    /* Connect to Wi-Fi */
AT+CFG=99,1234                        /* Set config parameter */
```

See [examples/test_vectors.at](examples/test_vectors.at) for supported data types including integers, strings, IP addresses, MAC addresses, byte arrays, and booleans.

## Interface Header

The tool parses a C interface header to resolve command IDs and type definitions. By default it uses the WINCS02 nc_driver header included in this repository (`WINCS02/driver/src/include/microchip_wincs02_intf.h`). Both the WINCS02 and RNWF02 headers contain the same command and type definitions, so either can be used.
