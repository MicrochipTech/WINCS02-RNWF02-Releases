"""
*******************************************************************************
NVM Update Utility for Microchip devices.

Copyright (c) 2026 Microchip Technology Inc. and its subsidiaries.
All rights reserved.

You may use this software and any derivatives exclusively with Microchip products.

THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER EXPRESS,
IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES
OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.
*******************************************************************************
"""

import argparse
import os
import time
import re
import serial

# ANSI color codes
C_GRAY = "\033[90m"
C_CYAN = "\033[96m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
#C_MAGENTA = "\033[95m"
C_RESET = "\033[0m"

TICK = C_GREEN + "✓" + C_RESET  # Green checkmark

BANNER = C_CYAN + """
RNWF02 NVM Update Utility
Copyright (c) 2026 Microchip Technology Inc. and its subsidiaries.
All rights reserved.
""" + C_RESET

DESCRIPTION = C_CYAN + 'Write data to RNWF02 device NVM via AT commands' + C_YELLOW

EPILOG = C_RESET + """
Examples:
  python %(prog)s -p COM5 rnwf02_ota.bin
  python %(prog)s -p COM5 -b 921600 firmware.bin --no-activate
"""

# Regular expression patterns
RE_NVMRD_HEX = rb'\+NVMRD:0x[0-9A-Fa-f]+,\d+,\[([0-9A-Fa-f]+)\]'
RE_NVMRD_STR = rb'\+NVMRD:0x[0-9A-Fa-f]+,\d+,\"(.*?)\"'
RE_ESCAPE_SEQ = rb'\\.'
RE_GMR_VERSION = rb'\+GMR:"([^"]*)"'

# Escape sequence mapping for string data
ESCAPE_MAP = {
    b'\\\\': b'\\',
    b'\\"': b'"',
    b'\\t': b'\t',
    b'\\r': b'\r',
    b'\\n': b'\n',
    b'\\a': b'\a',
    b'\\b': b'\b',
    b'\\v': b'\v',
    b'\\f': b'\f',
    b'\\e': b'\x1b',
    b'\\0': b'\0',
}

def gray_print(*args, **kwargs):
    """Print text in gray color for verbose/debug output"""
    print(C_GRAY, end='')
    print(*args, **kwargs)
    print(C_RESET, end='')

#.............................................................................

class FirmwareUpdate:
    """Handles firmware download to RNWF02 device via AT commands"""

    def __init__(self, args:argparse.Namespace):
        """Initialize firmware updater with serial connection"""
        self.args = args
        self.serial = serial.Serial(port=args.port, baudrate=args.baudrate, timeout=5)
        # set trace function based on verbose flag
        self.trace = gray_print if args.verbose else lambda *args, **kwargs: None

    def send_command(self, command:bytes, expected:bytes=b'OK\r\n', timeout:int=5) -> bytes:
        """Send AT command and wait for expected response"""
        # careful this can be glitchy
        if self.serial.timeout != timeout:
            self.serial.timeout = timeout
        self.trace("<", command)
        self.serial.write(command + b'\r\n')
        # returns available on timeout
        response = self.serial.read_until(expected)
        self.trace(">", response)
        # if we didnt get a good response then raise exception
        if not response.endswith(expected):
            raise RuntimeError(
                f"Unexpected response: '{response.decode(errors='ignore').strip()}'. "
                f"expected: '{expected.decode(errors='ignore').strip()}'")
        return response

    def check_communication(self):
        """Test AT communication with device"""
        print(f"\n{C_YELLOW}Checking device communication...{C_RESET}")
        # expect error for invalid command to flush any pending input
        self.send_command(b'!\r\nAT')
        print( f"{TICK} Device responding {self.serial.port} "
               f"at {self.serial.baudrate} bps")

    def erase_sectors(self, offset:int=0, sectors:int=240):
        """Erase NVM sectors"""
        print(f"\n{C_YELLOW}Erasing {sectors} sectors at offset {offset}...{C_RESET}")
        cmd = f'AT+NVMER={offset},{sectors}'
        self.send_command(cmd.encode(), expected=b'\r+NVMER\r\n', timeout=30)
        print(f"{TICK} Sectors erased successfully")

    def write_nvm(self, offset:int, data:bytes):
        """Write chunk of data to NVM at specified offset"""
        cmd = f'AT+NVMWR={offset:#010X},{len(data)},'
        cmd += '[' + ''.join(f'{byte:02X}' for byte in data) + ']'
        self.send_command(cmd.encode())

    def read_nvm(self, offset:int, length:int) -> bytes:
        """Read chunk of data from NVM at specified offset"""
        cmd = f'AT+NVMRD={offset:#010X},{length}'
        response = self.send_command(cmd.encode())
        # Extract hex data from response
        match = re.search(RE_NVMRD_HEX, response)
        if match:
            return bytes.fromhex(match.group(1).decode('ascii'))
        # Alternative format with string data
        match = re.search(RE_NVMRD_STR, response)
        if match:
            # Handle escaped characters in string (single-pass with regex)
            def replace_escape(m:re.Match) -> bytes:
                return ESCAPE_MAP.get(m.group(0), m.group(0))
            return re.sub(RE_ESCAPE_SEQ, replace_escape, match.group(1))
        # If no valid data found, raise error
        raise RuntimeError("Failed to read NVM data")

    def download_firmware(self):
        """Download firmware file to device"""

        def write_nvm_chunk(addr:int, chunk:bytes):
            """Helper to write NVM and possibly verify"""
            self.write_nvm(addr, chunk)
            if self.args.verify:
                read_back = self.read_nvm(addr, len(chunk))
                if read_back != chunk:
                    raise RuntimeError(
                        f"Verification failed at address {addr}:\n"
                        f"expected: {chunk.hex()}\ngot: {read_back.hex()}")

        print( f"\n{C_YELLOW}Downloading firmware from {self.args.firmware} "
               f"(chunk size: {self.args.chunk_size} bytes)...{C_RESET}")
        # Get file size for progress calculation
        file_size = os.path.getsize(self.args.firmware)
        total_chunks = (file_size + self.args.chunk_size - 1) // self.args.chunk_size
        start_time = time.time()
        # disable echo to improve performance
        self.send_command(b'ATE0')
        # Read and send file in chunks
        with open(self.args.firmware, "rb") as f:
            chunk_num = 0
            while True:
                chunk = f.read(self.args.chunk_size)
                if not chunk:
                    break
                addr = chunk_num * self.args.chunk_size
                write_nvm_chunk(addr, chunk)
                chunk_num += 1

                progress = (chunk_num * 100) // total_chunks
                print(
                    f"\rChunk {chunk_num}/{total_chunks} ({progress}%): "
                    f"{addr + len(chunk)}/{file_size} bytes",
                    end='', flush=True)
        # Final progress output
        elapsed = time.time() - start_time
        print(f"\r{TICK} Downloaded {file_size} bytes in {elapsed:.1f}s "
              f"({file_size/elapsed/1024:.1f} KB/s)")
        # re-enable echo
        self.send_command(b'ATE1')

    def verify_firmware(self):
        """Verify downloaded firmware image"""
        print(f"\n{C_YELLOW}Verifying firmware...{C_RESET}")
        self.send_command(b'AT+OTAVFY', expected=b'"Verify Done"\r\n')
        print(f"{TICK} Firmware verified successfully")

    def activate_firmware(self):
        """Activate the downloaded firmware image"""
        print(f"\n{C_YELLOW}Activating firmware...{C_RESET}")
        self.send_command(b'AT+OTAACT', expected=b'"Activate Done"\r\n')
        print(f"{TICK} Firmware activated successfully")

    def get_firmware_version(self):
        """Get firmware version information"""
        print(f"\n{C_YELLOW}Getting firmware version...{C_RESET}")
        response = self.send_command(b'AT+GMR')
        # Extract version string from +GMR:"..." line
        match = re.search(RE_GMR_VERSION, response)
        version = match.group(1).decode() if match else "Unknown"
        print(f"{TICK} Firmware version: {version}")

    def reset_device(self):
        """Reset the device"""
        print(f"\n{C_YELLOW}Resetting device...{C_RESET}")
        # +BOOT:"RNWF - AT Command Interface 3.2.0
        # (c) 2026 Microchip Technology Inc"
        self.send_command(b'AT+RST', expected=b'nology Inc"\r\n')
        print(f"{TICK} Device reset command sent")

    def update(self):
        """Complete firmware update procedure"""
        # Check if file exists before doing anything
        if not os.path.exists(self.args.firmware):
            raise RuntimeError(f"Firmware file not found: {self.args.firmware}")

        print(f"{C_YELLOW}Starting firmware update...{C_RESET}")
        self.check_communication()
        self.get_firmware_version()
        if self.args.erase:
            self.erase_sectors()
        self.download_firmware()
        if self.args.activate:
            self.verify_firmware()
            self.activate_firmware()
        if self.args.reset:
            self.reset_device()
            self.get_firmware_version()
        print(f"\n{TICK} Firmware update completed")

    def close(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()

#.............................................................................

def main():
    """Main entry point for the firmware updater"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG
    )

    parser.add_argument('-p', '--port',
                        required=True,
                        help='Serial port (e.g., COM5, /dev/ttyUSB0)')
    parser.add_argument('-b', '--baudrate',
                        type=int,
                        default=230400,
                        help='Baud rate (default: 230400)')
    parser.add_argument('-c', '--chunk-size',
                        type=int,
                        default=128,
                        help='Chunk size in bytes (default: 128)')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Enable verbose debug output')
    parser.add_argument('--no-erase',
                        action='store_false',
                        dest='erase',
                        help='Skip erasing sectors before download')
    parser.add_argument('--no-activate',
                        action='store_false',
                        dest='activate',
                        help='Skip firmware activation after download')
    parser.add_argument('--no-reset',
                        action='store_false',
                        dest='reset',
                        help='Skip device reset after firmware update')
    parser.add_argument('--read-verify',
                        action='store_true',
                        dest='verify',
                        help='Perform a read verification after writing each chunk')
    parser.add_argument('firmware',
                        help='Path to firmware binary file')

    print(BANNER)
    args = parser.parse_args()

    try:
        updater = FirmwareUpdate(args)
        updater.update()
        updater.close()
    except KeyboardInterrupt:
        print(f"\n\n{C_RED}Interrupted by user{C_RESET}")
    except (serial.SerialException, RuntimeError) as e:
        print(f"\n\n{C_RED}Error: {e}{C_RESET}")
        exit(1)

#.............................................................................

if __name__ == "__main__":
    main()
