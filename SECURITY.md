# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this software, please report it
responsibly through Microchip's official channels.

**Do not open a public GitHub issue for security vulnerabilities.**

### How to Report

Contact Microchip's Product Security Incident Response Team (PSIRT):

- **Email:** [psirt@microchip.com](mailto:psirt@microchip.com)
- **Web:** [https://www.microchip.com/design-centers/embedded-security/how-to-report-potential-product-security-vulnerabilities](https://www.microchip.com/design-centers/embedded-security/how-to-report-potential-product-security-vulnerabilities)

### What to Include

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Affected firmware version(s)
- Any relevant logs or screenshots

### Response

Microchip's PSIRT will acknowledge your report and work with you to
understand and address the issue. Please allow reasonable time for a
response before any public disclosure.

## Security Advisories

There are currently no published security vulnerabilities known to affect the **WINCS02** or **RNWF02** devices or their latest firmware.

Security enhancements and fixes have been applied to  **WINCS02** and **RNWF02** firmware in the following versions:

- **v3.1.0**
  - Fixed CVE-2009-3555 (TLS renegotiation)
  - Fixed CVE-2017-13079 and CVE-2017-13081 (Wi-Fi IGTK reinstallation)
  - Upgraded TLS stack to WolfSSL v5.7.4 from v4.7.0
  - Strengthened cryptographic elements used in Wi-Fi WPA2/WPA3 (NIST-standard RNG)

## Device Anti Rollback Feature

**WINCS02** and **RNWF02** devices include an Anti Rollback (ARB) feature. This can be used to prevent the device from running versions of firmware which are known to have security vulnerabilities.

The feature is based on the firmware version's Security Level:

| Security Level | Firmware Versions |
|---|---|
| 1 | v3.2.0, v3.1.0 |
| 0 | v3.0.0, v2.0.0, v1.0.0 |

For further details please refer to +ARB in the API Specification.
