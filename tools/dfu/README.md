# DFU (Device Firmware Update) Tool

The DFU tool (`do_dfu.py`) flashes firmware onto **WINCS02** and **RNWF02** devices
via a USB-to-UART bridge cable.

For full setup and usage instructions, see the
[DFU section of the Application Developer's Guide](https://onlinedocs.microchip.com/oxy/GUID-92FEB3A1-C10F-47DF-BF88-C06521800526-en-US-1/GUID-37EE4ED4-0BBE-4093-80FE-9F87C5DE740D.html).

## Quick Start

```bash
pip install -r requirements.txt
python do_dfu.py -b <product>_dfu_high.bin high
```
