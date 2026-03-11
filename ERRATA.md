# Current Errata for WINCS02 and RNWF02 Firmware

This file has information about known issues in the latest released **WINCS02** and **RNWF02** firmware.

## Latest Firmware

The latest released **WINCS02** and **RNWF02** firmware is [v3.2.0].

## Errata

These are the known issues in the latest released **WINCS02** and **RNWF02** firmware.

| Area | Description | ID | Recovery Method | Prevention Measure | Resulting impact |
|---|---|---|---|---|---|
| AP/Hotspot | The device deauthenticates a reconnecting STA if Management Frame Protection (MFP) is used | 1889 | Prompt the STA to retry the connection | None | With MFP enabled, some STAs may need two attempts to reconnect |
| TCP/IP | IPv6 multicast in received AMSDU can cause MAC Rx stall | 768 | None (no lasting effect) | None | Occasional reduction in Rx throughput |
