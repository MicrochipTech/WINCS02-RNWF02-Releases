"""
*******************************************************************************
AT FS-TSFR Utility Layer for Microchip devices.

Copyright (c) 2026 Microchip Technology Inc. and its subsidiaries.
All rights reserved.

You may use this software and any derivatives exclusively with Microchip products.

THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER EXPRESS,
IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES
OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.
*******************************************************************************
"""

from __future__ import annotations

import re
from typing import Callable

import serial

#.............................................................................

FOLDER_TYPES = {
    "user": 0,
    "cert": 1,
    "key": 2,
    "dh": 3,
    "cfg": 20,
}

# ANSI color codes for verbose trace output.
C_GRAY = "\033[90m"
C_RESET = "\033[0m"


def gray_print(*args, **kwargs):
    """Print text in gray color for verbose/debug output."""
    print(C_GRAY, end="")
    print(*args, **kwargs)
    print(C_RESET, end="")


# Matches FS handle/open response, e.g. b"+FS:1,7\r\n" -> (status=1, handle=7)
RE_FS_HANDLE = re.compile(rb"\+FS:(\d+),(\d+)\r\n")
# Matches one FS list entry, e.g. b"+FS:2,12,\"cert.pem\"\r\n" -> (len=12, name="cert.pem")
RE_FS_LIST = re.compile(rb"\+FS:2,(\d+),([^\r\n]+)\r\n")
# Matches FS info response, e.g. b"+FS:4,16384,8\r\n" -> (free_space, free_handles)
RE_FS_INFO = re.compile(rb"\+FS:4,(\d+),(\d+)\r\n")
# Matches FSTSFR load ack, e.g. b"+FSTSFR:1,2,256\r\n" -> (status, block_num, bytes_remaining)
RE_FSTSFR_LOAD = re.compile(rb"\+FSTSFR:(\d+),(\d+),(\d+)\r\n")
# Matches FSTSFR store block, e.g. b"+FSTSFR:1,2,0,[414243]\r\n" -> (..., payload)
RE_FSTSFR_STORE = re.compile(rb"\+FSTSFR:(\d+),(\d+),(\d+),(.+)\r\n")
# Matches firmware version response, e.g. b"+GMR:\"RNWF02 v1.0\"\r\nOK\r\n" -> (version)
RE_GMR = re.compile(rb'\+GMR:"(.+)"\r\nOK\r\n')
# Matches escaped char in quoted TSFR payload, e.g. b"\\n" or b"\\\""
RE_ESCAPE_SEQ = re.compile(rb"\\.")


ESCAPE_MAP = {
    b"\\\\": b"\\",
    b"\\\"": b'"',
    b"\\t": b"\t",
    b"\\r": b"\r",
    b"\\n": b"\n",
    b"\\a": b"\a",
    b"\\b": b"\b",
    b"\\v": b"\v",
    b"\\f": b"\f",
    b"\\e": b"\x1b",
    b"\\0": b"\0",
}

#.............................................................................

def _decode_tsfr_data(encoded: bytes) -> bytes:
    """Decode FS-TSFR payload from either [HEX] or quoted string format."""
    payload = encoded.strip()
    # Device may return raw bytes as hex wrapped in brackets: [414243] -> b"ABC".
    if payload.startswith(b"[") and payload.endswith(b"]"):
        return bytes.fromhex(payload[1:-1].decode("ascii"))

    # Quoted payload uses C-like escapes (\n, \t, \"), so unescape before returning.
    if payload.startswith(b'"') and payload.endswith(b'"'):
        inner = payload[1:-1]

        def replace_escape(match: re.Match[bytes]) -> bytes:
            return ESCAPE_MAP.get(match.group(0), match.group(0))

        return RE_ESCAPE_SEQ.sub(replace_escape, inner)

    return payload

#.............................................................................

class AtTransfer:
    """Serial AT interface wrapper for RNWF02 filesystem commands."""

    def __init__(
        self,
        port: str,
        baudrate: int = 230400,
        timeout: float = 1.0,
        verbose: bool = False,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.verbose = verbose
        self.serial: serial.Serial | None = None
        self.trace: Callable[..., None] = gray_print if verbose else lambda *a, **k: None

    # Connection lifecycle.

    def open(self) -> None:
        """Open serial connection if not already open."""
        #if self.serial and self.serial.is_open:
        #    return
        try:
            # pyserial object is created lazily so callers can configure first.
            self.serial = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            raise RuntimeError(
                f"Failed to open serial port '{self.port}'") from e

    def close(self) -> None:
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()

    # Context-manager usage: with AtTransfer(...) as at:

    def __enter__(self) -> AtTransfer:
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # Generic command/response helpers.

    def send_command(
        self,
        command: str | bytes,
        expected: bytes = b"OK\r\n",
        timeout: float | None = None,
    ) -> bytes:
        """Send AT command and wait until the expected trailer is read."""
        #self.open()
        assert self.serial is not None
        # avoid mutating shared serial object if caller didn't specify a timeout override
        if timeout is not None and self.serial.timeout != timeout:
            self.serial.timeout = timeout
        # Normalize command to bytes, append CRLF, and wait for the expected trailer.
        cmd = command if isinstance(command, bytes) else command.encode("ascii")
        self.trace("<", cmd)
        self.serial.write(cmd + b"\r\n")
        response = self.serial.read_until(expected)
        self.trace(">", response)
        # Note that read_until returns all data up to and including the expected trailer
        # also if timeout occurs then it returns whatever data was received
        if not response.endswith(expected):
            raise RuntimeError(
                f"Unexpected response: '{response.decode(errors='ignore').strip()}'. ")
        return response


    def check_communication(self) -> None:
        """Check if module responds to AT command."""
        try:
            # First command clears possible prompt state, second confirms normal AT flow.
            self.send_command("!\r\nAT")
            self.send_command("ATE0")  # disable echo for cleaner responses
        except RuntimeError as e:
            raise RuntimeError(
                f"Failed to communicate with device on {self.port}") from e

    def gmr(self) -> str:
        """Get module version string."""
        # GMR response includes version string in capture group 1.
        response = self.send_command("AT+GMR")
        match = RE_GMR.search(response)
        if not match:
            raise RuntimeError("Failed to parse GMR response")
        return match.group(1).decode("utf-8", errors="replace").strip()

    # Filesystem metadata operations.

    def fs_list(self, folder_type: int) -> list[str]:
        """List files in filesystem folder."""
        # FS list response includes one line per entry with name in capture group 2
        response = self.send_command(f"AT+FS=2,{folder_type}")
        names: list[str] = []
        for match in RE_FS_LIST.finditer(response):
            name = match.group(2).decode("utf-8", errors="replace").strip()
            #if len(name) >= 2 and name[0] == '"' and name[-1] == '"':
            #    name = name[1:-1]
            # Firmware returns names quoted, so drop surrounding quote characters.
            names.append(name[1:-1])
        return names


    def fs_info(self) -> tuple[int, int]:
        """Return (free_space, free_handles)."""
        # FS info response includes free space and free handle count in capture groups 1 and 2.
        response = self.send_command("AT+FS=4")
        match = RE_FS_INFO.search(response)
        if not match:
            raise RuntimeError("Failed to parse FS info response")
        return int(match.group(1)), int(match.group(2))


    def fs_delete(self, folder_type: int, name: str) -> None:
        """Delete a file from filesystem folder."""
        # Firmware expects name to be quoted
        self.send_command(f'AT+FS=3,{folder_type},"{name}"')

    # Transfer-write path (host -> module).

    def _fstsfr_extract_handle(self, response: bytes) -> int:
        # FS open/create response includes transfer handle in capture group 2.
        match = RE_FS_HANDLE.search(response)
        if not match:
            raise RuntimeError("Failed to parse FS transfer handle")
        return int(match.group(2))


    def _fstsfr_send_block(self, handle: int, block_num: int, data: bytes) -> int:
        """Send one load block and return bytes remaining."""
        # Load transfer expects block payload encoded as uppercase hex in brackets.
        payload = "[" + data.hex().upper() + "]"
        response = self.send_command(f"AT+FSTSFR={handle},{block_num},{payload}")
        match = RE_FSTSFR_LOAD.search(response)
        if not match:
            raise RuntimeError("Failed to parse load block response")
        return int(match.group(3))

    def fs_load(self, folder_type: int, name: str, data: bytes, block_size: int = 128) -> None:
        """Load a local byte buffer into remote filesystem file."""
        # start the transfer session and get the handle
        cmd = f'AT+FS=1,{folder_type},5,"{name}",{len(data)}'
        response = self.send_command(cmd)
        handle = self._fstsfr_extract_handle(response)
        # transfer the data in blocks until all bytes are sent or an error occurs
        # nb blocksize must be 128 for this to work
        block_num = 1
        bytes_remaining = len(data)
        while bytes_remaining > 0:
            # Slice next chunk, send it, then trust module-reported bytes_remaining.
            chunk = data[:block_size]
            data = data[block_size:]
            bytes_remaining = self._fstsfr_send_block(handle, block_num, chunk)
            block_num += 1
        # Final AT+FSTSFR with no args closes/checks the transfer session.
        self.send_command("AT+FSTSFR")

    # Transfer-read path (module -> host).

    def _fstsfr_read_block(self, handle: int, block_num: int, data_length: int) -> tuple[int, bytes]:
        """Read one store block and return (bytes_remaining, data)."""
        # Store transfer block response includes payload in capture group 4 and bytes_remaining in group 3.
        response = self.send_command(f"AT+FSTSFR={handle},{block_num},{data_length}")
        match = RE_FSTSFR_STORE.search(response)
        if not match:
            raise RuntimeError("Failed to parse store block response")
        bytes_remaining = int(match.group(3))
        # Payload may be bracketed HEX or quoted escaped bytes; normalize both forms.
        data = _decode_tsfr_data(match.group(4))
        return bytes_remaining, data

    def fs_store(self, folder_type: int, name: str, block_size: int = 128) -> bytes:
        """Store a remote filesystem file into local byte buffer."""
        # start the transfer session and get the handle
        cmd = f'AT+FS=5,{folder_type},5,"{name}"'
        response = self.send_command(cmd)
        handle = self._fstsfr_extract_handle(response)
        # transfer the data in blocks until all bytes are sent or an error occurs
        block_num = 1
        bytes_remaining = 1
        # Buffer is assembled incrementally because each AT response carries one block.
        out = bytearray()
        while bytes_remaining > 0:
            # Keep requesting sequential blocks until module reports zero remaining.
            bytes_remaining, block = self._fstsfr_read_block(handle, block_num, block_size)
            out.extend(block)
            block_num += 1
        # Final AT+FSTSFR with no args closes/checks the transfer session.
        self.send_command("AT+FSTSFR")
        # return the data as bytes
        return bytes(out)
