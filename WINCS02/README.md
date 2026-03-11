# WINCS02 — Wi-Fi Network Controller Module (SPI)

The **WINCS02** is a Wi-Fi network controller device with an SPI host interface
using a binary TLV protocol (nc_driver).

## Firmware

Firmware binaries and release notes are available on the [Releases page](../../releases).

| Version | Download |
|---------|----------|
| **v3.2.0** (latest) | [GitHub Release](../../releases/tag/WINCS02_v3.2.0) |

### Firmware Files

Each release contains the following binaries:

| File | Description | Usage |
|---|---|---|
| `wincs02_wholeflash.bin` | Full flash image (firmware + empty slot + file system) | Use with the [DFU tool](../tools/dfu/) or a host application to programme the firmware and file system on a non-running device |
| `wincs02_dfu_high.bin` | Activated firmware image (single slot) | Use with the [DFU tool](../tools/dfu/) or a host application to update the firmware on a non-running device |
| `wincs02_ota.bin` | Firmware image (single slot) | Use with a host application to update the firmware on a running device |
| `flfs_image.bin` | File system image containing default TLS certificates | Use with the [DFU tool](../tools/dfu/) or a host application to update the file system on a non-running device |

## Documentation

- [Binary Protocol API Specification (PDF)](doc/WINCS02_API_Reference.pdf) — complete protocol reference
- [Application Developer's Guide](https://onlinedocs.microchip.com/g/GUID-B7A95EBE-7BB2-4AF4-A525-700FB718E47A) — getting started, examples, DFU instructions
- [Data Sheet (PDF)](https://ww1.microchip.com/downloads/aemDocuments/documents/WSG/ProductDocuments/DataSheets/WINCS02-Wi-Fi-Module-Data-Sheet-DS70005577.pdf)

## Host Driver

The [SPI nc_driver](driver/) is a standalone binary protocol driver for communicating
with the WINCS02 over SPI. It can be used on any MCU/RTOS with no MPLAB Harmony
dependency.

See the [driver README](driver/README.md) for API overview and porting guide.

## Add-on Board

The **WINCS02** Add-on Board ([EV68G27A](https://www.microchip.com/en-us/development-tool/ev68g27a))
provides a ready-to-use evaluation platform with SPI headers.

## MPLAB Harmony Resources

- [wireless_wifi](https://github.com/Microchip-MPLAB-Harmony/wireless_wifi) — driver layer (includes **WINCS02** driver at `driver/wincs02/`)
- [wireless_system_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_system_rnwf) — Wi-Fi, MQTT, Net, OTA system services (supports both **RNWF02** and **WINCS02**)
- [wireless_apps_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_apps_rnwf) — example applications

> **Note:** Despite the `rnwf` in their names, the Harmony repos support both
> **RNWF02** and **WINCS02**. The **WINCS02** driver lives in `wireless_wifi`; the
> `wireless_system_rnwf` services layer is optional.
