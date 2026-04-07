# WINCS02 SPI nc_driver

Portable C driver library for communicating with the WINCS02 module via SPI.

## Overview

This driver (nc_driver) provides a host-side library for the WINCS02 binary
protocol over SPI. It can run on any MCU with a standard SPI peripheral — no
MPLAB Harmony dependency.

## Directory Structure

```
driver/
├── README.md       # This file
├── src/            # Core driver source (do not modify)
│   ├── *.c         # 6 source files
│   └── include/    # Driver headers
├── port/           # Platform porting layer — start here
│   ├── winc_port_template.c   # SPI, GPIO, init, and event-loop template
│   └── conf_winc_dev.h        # Standalone configuration (bare-metal ready)
└── examples/       # Example usage
```

## Quick Start

### What you need to implement

| Function | Purpose |
|----------|---------|
| SPI send/receive | Full-duplex SPI transfer with CS management |
| MCLR pin control | Drive reset pin low/high |
| INTOUT pin read | Check if interrupt pin is asserted (low) |
| Delay | Blocking millisecond delay |
| Debug printf | Optional but highly recommended for bring-up |

### Porting steps

1. **Copy** `port/winc_port_template.c` into your project and implement
   the five platform functions for your MCU.

2. **Copy** `port/conf_winc_dev.h` into your project include path.
   Adjust `WINC_DEV_CACHE_LINE_SIZE` for your MCU (set to 1 if no cache).

3. **Add** all `.c` files from `src/` and your porting file to your build.
   Add `src/include/` and your config file location to the include path.

4. **Build.** The driver compiles with GCC, IAR, and XC32. No source
   modifications are needed.

The template file contains a complete commented-out example showing the full
init sequence and event loop — uncomment and adapt for your application.

## SPI Requirements

| Parameter | Value |
|-----------|-------|
| Mode | 0 (CPOL=0, CPHA=0) |
| Bit order | MSB first |
| Max clock | 50 MHz (datasheet Table 3-11; actual max depends on layout) |
| CS control | Assert (low) at start, deassert (high) at end of **each** call |
| Dummy TX byte | **0xFF** (WINCS02 interprets 0x00 as valid data) |

When `pTransmitData` is NULL, your implementation **must send 0xFF** for each
byte. This is the single most common cause of communication failures.

## Initialisation Sequence

```
1. Platform init         — configure SPI, GPIO for MCLR + INTOUT + CS
2. MCLR reset            — drive low 100ms, release high
3. Wait for boot         — WINCS02 takes ~3.5s to boot after MCLR release
                           (MISO reads 0x00 during boot, transitions to 0xFF when ready)
4. WINC_DevInit()        — create driver context with receive buffer
5. WINC_SDIODeviceInit() — handshake over SPI (retry loop with 100ms delays)
6. WINC_DevBusStateSet() — set bus to ACTIVE (required before sending commands)
7. Register callbacks    — WINC_DevAECCallbackRegister() for async events
8. Event loop            — poll INTOUT, call WINC_DevHandleEvent() + WINC_DevUpdateEvent()
```

Steps 5-8 are shown in detail in `winc_port_template.c`.

## SDIO Init Status Codes

`WINC_SDIODeviceInit()` returns a signed enum. Your retry loop must handle:

| Status | Value | Meaning | Action |
|--------|-------|---------|--------|
| `OK` | 0 | Complete | Proceed to step 6 |
| `RESET_WAITING` | 1 | Module still booting | Delay 100ms, retry |
| `OP_WAITING` | 2 | CMD5 in progress | Delay 100ms, retry |
| `OP_FAILED` | -4 | CMD5 failed | Reset `sdioState` to `UNKNOWN`, retry |
| `RESET_FAILED` | -5 | CMD0 bad response | Check wiring, reset state, retry |
| `ERROR` | -2 | Unrecoverable | Hard-reset the module |

A tight retry loop without delays will burn CPU for ~3.5 seconds. Always
include a delay (e.g. 100ms) between retries.

## Hardware Connections

### Required signals

| Signal | WINCS02 Module Pin | Direction | Description |
|--------|-------------------|-----------|-------------|
| CS | 16 (CS1) | Host → Module | SPI chip select, active low |
| SCK | 18 (SCK1) | Host → Module | SPI clock |
| MOSI | 15 (SDI1) | Host → Module | SPI data in to module |
| MISO | 17 (SDO1) | Module → Host | SPI data out from module |
| MCLR | 4 | Host → Module | Master clear reset, active low |
| INTOUT | 13 | Module → Host | Interrupt request, active low, push-pull |

### External components (bare module only)

If using the bare WINCS02 module (not the Add-On Board), you must provide:

| Component | Pin | Value | Purpose |
|-----------|-----|-------|---------|
| Pull-up resistor | MCLR (pin 4) | 10K to VDD | Holds module out of reset |
| Pull-up resistor | STRAP1 (pin 10) | 10K to VDD | Selects SPI host interface |
| Pull-up resistor | STRAP2 (pin 26) | 10K to VDD | Selects SPI host interface |
| Decoupling cap | VDD (pin 20) | 4.7uF + 0.1uF | Power supply filtering |
| Decoupling cap | VDDIO (pin 23) | 0.1uF | I/O supply filtering |
| Tristate I/O | Pin 11 (Reserved) | — | Datasheet requires connection |

The **WINCS02 Add-On Board (EV68G27A)** includes all of these — just connect
the mikroBUS header signals and ground.

### WINCS02 Add-On Board (EV68G27A) connections

If using the add-on board, connect these mikroBUS pins to your host MCU:

| Add-On Board Pin | mikroBUS Label | Host MCU Pin | Signal |
|-----------------|---------------|-------------|--------|
| J204 pin 6 | MOSI | SPI MOSI (TX) | SPI data to module |
| J204 pin 5 | MISO | SPI MISO (RX) | SPI data from module |
| J204 pin 4 | SCK | SPI CLK | SPI clock |
| J204 pin 3 | CS | GPIO output | Chip select |
| J204 pin 2 | RST | GPIO output | MCLR reset |
| J205 pin 2 | INT | GPIO input | INTOUT interrupt |
| J204 pin 8 | GND | GND | **Common ground (mandatory)** |

Power the add-on board via its USB Type-C connector. Set jumper JP200 to
the USB position.

## Bare-Metal Configuration

For bare-metal (no RTOS), the provided `port/conf_winc_dev.h` works
out of the box. The lock macros are left undefined, which activates the
driver's built-in no-op defaults (`winc_dev.h` lines 44-58).

## MPLAB Harmony Users

If you are using MPLAB Harmony, use the integrated driver and services:
- [wireless_wifi](https://github.com/Microchip-MPLAB-Harmony/wireless_wifi) — WINCS02 driver at `driver/wincs02/`
- [wireless_system_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_system_rnwf) — system services
- [wireless_apps_rnwf](https://github.com/Microchip-MPLAB-Harmony/wireless_apps_rnwf) — example applications

> **Note:** The WINCS02 driver lives in `wireless_wifi`; the
> `wireless_system_rnwf` services layer is optional.

## API Specification

See the Binary Protocol API Specification ([PDF](../doc/WINCS02_API_Reference.pdf), [Markdown](../doc/WINCS02_API_Reference.md)) for the
complete protocol reference.

## Troubleshooting

| Symptom | Likely Cause |
|---------|-------------|
| SDIO init returns `RESET_WAITING` forever | Module still booting — wait longer (needs ~3.5s after MCLR) |
| SDIO init returns `RESET_FAILED` | SPI wiring wrong, MOSI/MISO swapped, or CS not toggling |
| SPI test reads 0x00 after boot complete | GND not connected between boards |
| Commands sent but no AEC events received | `WINC_DevBusStateSet(ACTIVE)` not called, or INTOUT not polled |
| `WINC_DevInit()` returns invalid handle | Receive buffer is NULL or too small |
| Scan/connect commands fail silently | Command buffer freed before `STATUS_COMPLETE` callback |
