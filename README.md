# WINCS02 & RNWF02 — Firmware, Drivers & Tools

Microchip **WINCS02** and **RNWF02** are Wi-Fi network controller devices available via [microchip.com](https://www.microchip.com).

This repository is the central hub for the latest firmware and programming resources:

- [**Firmware Release Packages**](../../releases) — GitHub releases containing firmware binaries and release notes
- [**Tools**](./tools/) — Tools for programming and updating firmware and files on the devices
- [**Host Driver**](./WINCS02/driver/) — The standalone driver for host MCUs to interface to the **WINCS02** device

## Device Summary
**WINCS02** and **RNWF02** are Wi-Fi network controller devices that offload Wi-Fi and networking from the host MCU or terminal. The host communicates with the module over a simple serial interface — SPI for WINCS02 or UART for RNWF02 — while the module handles 802.11 connectivity, TCP/IP, TLS, MQTT, HTTP, OTA updates, and more.

**WINCS02** and **RNWF02** devices differ from each other in terms of their host interface:

| | WINCS02 | RNWF02 |
|---|---|---|
| **Host Interface** | SPI | UART |
| **Protocol** | Binary TLV (via nc_driver) | ASCII AT Commands |

## Device Features
**WINCS02** and **RNWF02** provide the following features:

- **Wi-Fi:** 802.11 b/g/n, station and soft-AP modes, WPA2/WPA3 Personal & Enterprise, simple roaming
- **TCP/IP Stack:** IPv4/IPv6, TCP, UDP, DHCP client/server, DNS client
- **TLS:** TLS 1.2 client/server
- **MQTT:** MQTT v3.1.1 / v5.0 client with TLS support
- **HTTP/S:** HTTP client for REST APIs and cloud connectivity
- **SNTP:** Network time synchronization
- **Low Power:** Wi-Fi and system level power-save modes
- **Bypass Mode:** Layer 2 raw packet send/receive with unicast/broadcast/multicast filtering
- **Coexistence:** BLE/Wi-Fi coexistence arbiter
- **Internal Flash Memory:** Active and rollback firmware images, per-device calibration data, 60KB on-chip file system
- **File System:** Access to on-chip flash file system (FLFS) for TLS certificates, keys, and configuration files
- **Firmware Programming Options:**
  - **Device Firmware Update (DFU):** Firmware programming of a non-running device
  - **Over-the-air (OTA):** Firmware updates of a running device
- **Secure Boot:** Immutable secure boot with hardware root of trust
- **Anti Rollback:** Protection from historically vulnerable firmware

## Firmware Programming and Updating
Firmware can be programmed or updated on non-running **WINCS02** and **RNWF02** devices:
- via the [DFU tool](../tools/dfu/); or
- via a host application that implements the DFU process described in the application developer guide.

Firmware can be updated on running **WINCS02** and **RNWF02** devices:
- via the [NVM Update tool](../tools/nvm_update/); or
- via a host application that implements OTA as described in the API specification.

## Quick Links

| WINCS02 | RNWF02 |
|---|---|
| [Latest Firmware Release Package](../../releases/tag/WINCS02_v3.2.0) |[Latest Firmware Release Package](../../releases/tag/RNWF02_v3.2.0) | 
| [Host Driver](./WINCS02/driver/) | N/A |
| [API Specification (Binary Protocol)](./WINCS02/doc/WINCS02_API_Reference.pdf) | [API Specification (AT Command)](./RNWF02/doc/RNWF02_AT_Command_Reference.pdf) |
| [Application Developer Guide](https://onlinedocs.microchip.com/g/GUID-B7A95EBE-7BB2-4AF4-A525-700FB718E47A) | [Application Developer Guide](https://onlinedocs.microchip.com/g/GUID-92FEB3A1-C10F-47DF-BF88-C06521800526) |
| [Data Sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/WSG/ProductDocuments/DataSheets/WINCS02-Wi-Fi-Module-Data-Sheet-DS70005577.pdf) | [Data Sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/WSG/ProductDocuments/DataSheets/RNWF02-Wi-Fi-Module-Data-Sheet-DS70005544.pdf) |

| WINCS02 and RNWF02 |
|---|
| [Errata](./ERRATA.md) |
| [Changelog](./CHANGELOG.md) |


## Getting Notifications

Click **Watch** → **Custom** → **Releases** to receive email notifications
when new firmware is published.
