# RNWF02 — Wi-Fi Network Controller Module (UART)

The **RNWF02** is a Wi-Fi network controller device with a UART host interface
using ASCII AT commands.

## Firmware

Firmware binaries and release notes are available on the [Releases page](../../releases).

| Version | Download |
|---------|----------|
| **v3.2.0** (latest) | [GitHub Release](../../releases/tag/RNWF02_v3.2.0) |

### Firmware Files

Each release contains the following binaries:

| File | Description | Usage |
|---|---|---|
| `rnwf02_wholeflash.bin` | Full flash image (firmware + empty slot + file system) | Use with the [DFU tool](../tools/dfu/) or a host application to programme the firmware and file system on a non-running device |
| `rnwf02_dfu_high.bin` | Activated firmware image (single slot) | Use with the [DFU tool](../tools/dfu/) or a host application to update the firmware on a non-running device |
| `rnwf02_ota.bin` | Firmware image (single slot) | Use with the [NVM Update tool](../tools/nvm_update/) or a host application to update the firmware on a running device |
| `flfs_image.bin` | File system image containing default TLS certificates | Use with the [DFU tool](../tools/dfu/) or a host application to update the file system on a non-running device |

## Documentation

- [AT Command API Specification (PDF)](doc/RNWF02_AT_Command_Reference.pdf) — complete command reference
- [Application Developer's Guide](https://onlinedocs.microchip.com/g/GUID-92FEB3A1-C10F-47DF-BF88-C06521800526) — getting started, examples, DFU instructions
- [Data Sheet (PDF)](https://ww1.microchip.com/downloads/aemDocuments/documents/WSG/ProductDocuments/DataSheets/RNWF02-Wi-Fi-Module-Data-Sheet-DS70005544.pdf)

## Add-on Board

The RNWF02 Add-on Board ([EV72E72A](https://www.microchip.com/en-us/development-tool/ev72e72a))
provides a ready-to-use evaluation platform with USB-UART bridge and mikroBUS headers.

## MPLAB Harmony Resources

- [wireless_system_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_system_rnwf) — Wi-Fi, MQTT, Net, OTA system services
- [wireless_apps_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_apps_rnwf) — example applications
