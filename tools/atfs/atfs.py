"""
*******************************************************************************
Filesystem Utility for Microchip devices.

Copyright (c) 2026 Microchip Technology Inc. and its subsidiaries.
All rights reserved.

You may use this software and any derivatives exclusively with Microchip products.

THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER EXPRESS,
IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES
OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.
*******************************************************************************
"""

import argparse
import re
from pathlib import Path

from atfs_tsfr import AtTransfer, FOLDER_TYPES

#.............................................................................

# ANSI color codes
C_GRAY = "\033[90m"
C_CYAN = "\033[96m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

TICK = C_GREEN + "✓" + C_RESET
#TICK = C_GREEN + "*" + C_RESET

FOLDERS = FOLDER_TYPES

DEFAULT_BAUDRATE = 230400

BANNER = C_CYAN + """
RNWF02 File System Utility
Copyright (c) 2026 Microchip Technology Inc. and its subsidiaries.
All rights reserved.
""" + C_RESET

DESCRIPTION = C_CYAN + "Manage RNWF02 filesystem over UART using AT+FS and AT+FSTSFR" + C_YELLOW

EPILOG = C_RESET + f"""
Commands:
    load folder path [name]
    list folder
    delete folder name
    info
    store folder name [path] [--force]

Folders:
    user, cert, key, dh, cfg

Common options:
    -p, --port      Serial port (required)
    -b, --baudrate  Baud rate (default: 230400)
    -v, --verbose   Print AT command trace

Examples:
    {C_GRAY}# Show filesystem status{C_RESET}
    python %(prog)s -p COM6 info
    {C_GRAY}# Load with explicit device filename{C_RESET}
    python %(prog)s -p COM6 load user c:/certs/device.crt device_crt
    {C_GRAY}# Load and auto-generate device filename from local file stem{C_RESET}
    python %(prog)s -p COM6 load cfg c:/rnwf/autoexec.txt
    {C_GRAY}# Use custom baudrate and verbose trace output{C_RESET}
    python %(prog)s -p COM6 -b 921600 -v load user c:/data/blob.bin blob_bin
    {C_GRAY}# List files in remote folder{C_RESET}
    python %(prog)s -p COM6 list cert
    {C_GRAY}# Delete remote file{C_RESET}
    python %(prog)s -p COM6 -b 921600 delete cfg file1
    {C_GRAY}# Store to explicit local file path{C_RESET}
    python %(prog)s -p COM6 store cfg autoexec c:/out/autoexec
    {C_GRAY}# Store to directory (output file will use remote name){C_RESET}
    python %(prog)s -p COM6 store cfg autoexec c:/out/
    {C_GRAY}# Store with default local path (uses remote name in current directory){C_RESET}
    python %(prog)s -p COM6 store cfg autoexec
    {C_GRAY}# Allow overwrite of existing local output file{C_RESET}
    python %(prog)s -p COM6 store cfg autoexec c:/folder/cfg/ --force
"""


#.............................................................................

class FileSystemUtility:
    """RNWF02 filesystem command runner."""

    def __init__(self, args: argparse.Namespace):
        # Keep parsed CLI arguments available to every command handler.
        self.args = args

    def validate(self):
        """Validate command arguments before command execution."""

        def validate_device_name():
            # RNWF firmware is stricter than the generic string syntax and rejects
            # names with extension-like dots for FS-TSFR operations.
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.args.name):
                raise RuntimeError(
                    "Invalid device filename. Use 1-32 chars: letters, digits, '_' or '-'. " )

        def validate_load():
            # Validate local source file before upload.
            # check that the file exists
            if not Path(self.args.path).is_file():
                raise RuntimeError(
                    f"Local file not found: {self.args.path}")
            # ... and is not empty
            if Path(self.args.path).stat().st_size <= 0:
                raise RuntimeError(
                    "Local file is empty. FS-TSFR requires file size > 0.")
            # if no device name specified then generate one based on the local file name
            if not self.args.name:
                self.args.name = Path(self.args.path).stem
            # validate we are not trying to write a silly name
            ##validate_device_name()

        def validate_store():
            # Validate local destination path before download.
            # check we are not reading from key folder this is prohibited
            if self.args.folder == "key":
                raise RuntimeError(
                    "Storing files from 'key' folder is not allowed for security reasons.")
            # if user didnt specify the file then autogenerate a name based on the device file name
            if not self.args.path:
                self.args.path = self.args.name
                #return
            # check parent folder exists and is a directory
            if not Path(self.args.path).parent.is_dir():
                raise RuntimeError(
                    f"Local output directory does not exist: {Path(self.args.path).parent}")
            # suppose user just specfied a directory as the path, in this case we will write
            #  the file to that directory with the device name as the filename
            if Path(self.args.path).is_dir():
                self.args.path = str(Path(self.args.path) / self.args.name)
            # protect local files by default unless the user explicitly opts in
            if self.args.check_overwrite and Path(self.args.path).exists():
                raise RuntimeError(
                    f"Local output path already exists: {self.args.path}. "
                    "Use --force to allow replacing it.")

        # Apply command-specific validation only for commands that need it.
        if self.args.command == "load":
            validate_load()
        if self.args.command == "store":
            validate_store()
        # ensure device filename is valid for commands that use it
        if self.args.command in ("load", "store", "delete"):
            # check that the device name is sensible
            validate_device_name()


    def run(self):
        """Run selected command using active serial AT session."""
        # show the user what we parsed from the command line before we start doing things
        print(
            f"{TICK} CLI parsed:"
            f" command={self.args.command}"
            f" port={self.args.port}"
            f" baudrate={self.args.baudrate}"
            f" verbose={self.args.verbose}" )

        # Open one AT session and keep it for the entire command.
        with AtTransfer(
            port=self.args.port,
            baudrate=self.args.baudrate,
            verbose=self.args.verbose,
        ) as at:
            # check we can talk to the device before trying to run any commands
            at.check_communication()
            print(f"{TICK} Device communication established")
            print(f"{TICK} Device version: {at.gmr()}")

            # Dispatch to the selected subcommand handler.
            if self.args.command == "load":
                self.command_load(at)
            elif self.args.command == "list":
                self.command_list(at)
            elif self.args.command == "delete":
                self.command_delete(at)
            elif self.args.command == "info":
                self.command_info(at)
            elif self.args.command == "store":
                self.command_store(at)
            # pull folder command to download all files??


    def command_load(self, at: AtTransfer):
        """Transfer local file to device."""
        # show the user what we are about to load before we do it
        print(f"{TICK} Folder: {self.args.folder} (type {FOLDERS[self.args.folder]})")
        print(f"{TICK} Local file: {self.args.path}")
        print(f"{TICK} Device filename: {self.args.name}")
        # Read file into a buffer for transfer. check for failures
        try:
            data = Path(self.args.path).read_bytes()
        except OSError as e:
            raise RuntimeError(
                f"reading file: {e}") from e
        print(f"{TICK} Loaded {len(data)} bytes from {Path(self.args.path).resolve()}")
        # Send file bytes to the module in FS-TSFR blocks.
        at.fs_load(
            folder_type=FOLDERS[self.args.folder],
            name=self.args.name,
            data=data,
            ##block_size=self.args.block_size,
        )
        print(f"{TICK} Load command completed")


    def command_list(self, at: AtTransfer):
        """List files from a device folder."""
        # show the user what we are about to list before we do it
        print(f"{TICK} Folder: {self.args.folder} (type {FOLDERS[self.args.folder]})")
        # Query file list from the selected remote folder.
        names = at.fs_list(FOLDERS[self.args.folder])
        print(f"{TICK} List command completed")
        # now show the user what we found - if anything
        if names:
            print()
            for name in names:
                print(f"{C_YELLOW}{name}{C_RESET}")
        # and show the count of files found
        print()
        print(f"{C_YELLOW}{len(names)} File(s) found{C_RESET}")


    def command_delete(self, at: AtTransfer):
        """Delete a file from device."""
        # show what we are about to delete before we do it
        print(f"{TICK} Folder: {self.args.folder} (type {FOLDERS[self.args.folder]})")
        print(f"{TICK} Device filename: {self.args.name}")
        # Issue delete command for one file in the selected folder.
        at.fs_delete(FOLDERS[self.args.folder], self.args.name)
        print(f"{TICK} Delete command completed")


    def command_info(self, at: AtTransfer):
        """Query filesystem information."""
        # Read free-space and handle counters from the module.
        free_space, free_handles = at.fs_info()
        print(f"{TICK} Info command completed")
        # now show the user the results we got back from the device
        print()
        print(f"{C_YELLOW}Free space: {free_space}{C_RESET}")
        print(f"{C_YELLOW}Free handles: {free_handles}{C_RESET}")


    def command_store(self, at: AtTransfer):
        """Transfer file from device to local machine."""
        # dump out information of transfer about to be performed before starting it
        print(f"{TICK} Folder: {self.args.folder} (type {FOLDERS[self.args.folder]})")
        print(f"{TICK} Device filename: {self.args.name}")
        print(f"{TICK} Local output: {self.args.path}")
        # Read bytes from the module using FS-TSFR.
        data = at.fs_store(
            folder_type=FOLDERS[self.args.folder],
            name=self.args.name,
            ##block_size=self.args.block_size,
        )
        # write the data to local file system - check for failures
        try:
            Path(self.args.path).write_bytes(data)
        except OSError as e:
            raise RuntimeError(
                f"writing file: {e}") from e
        # inform the user of the successful transfer and where we put the file
        print(f"{TICK} Stored {len(data)} bytes to {Path(self.args.path).resolve()}")
        print(f"{TICK} Store command completed")


#.............................................................................

def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    # Keep help text verbose with examples and command-specific syntax.
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )

    parser.add_argument(
        "-p",
        "--port",
        required=True,
        help="Serial port (e.g., COM6, /dev/ttyUSB0)",
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help=f"Baud rate (default: {DEFAULT_BAUDRATE})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug output",
    )

    # Each subparser maps to one FileSystemUtility method via run() dispatch.
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Upload local file to device.
    parser_load = subparsers.add_parser("load", help="Transfer local file to device")
    parser_load.add_argument("folder", choices=FOLDERS.keys(), help="Remote folder")
    parser_load.add_argument("path", help="Local input file path")
    parser_load.add_argument(
        "name",
        nargs="?",
        help="Optional device filename (letters/digits/_/- only)",
    )

    # List all files in a remote folder.
    parser_list = subparsers.add_parser("list", help="List files in remote folder")
    parser_list.add_argument("folder", choices=FOLDERS.keys(), help="Remote folder")

    # Delete a single remote file.
    parser_delete = subparsers.add_parser("delete", help="Delete file on device")
    parser_delete.add_argument("folder", choices=FOLDERS.keys(), help="Remote folder")
    parser_delete.add_argument("name", help="Device filename (letters/digits/_/- only)")

    # Query device filesystem counters.
    subparsers.add_parser("info", help="Show filesystem information")

    # Download remote file to a local path.
    parser_store = subparsers.add_parser("store", help="Transfer file from device to local")
    # q: is there a way to remove key from the choices here ?
    # maybe we can just allow it here and then give a nice error message if user tries to use it?
    parser_store.add_argument("folder", choices=FOLDERS.keys(), help="Remote folder")
    parser_store.add_argument("name", help="Device filename (letters/digits/_/- only)")
    parser_store.add_argument("path", nargs="?", help="Optional local output path")
    parser_store.add_argument(
        "--force",
        dest="check_overwrite",
        action="store_false",
        help="Allow overwriting an existing local output file",
    )
    parser_store.set_defaults(check_overwrite=True)

    return parser


def main() -> int:
    """Main entry point for filesystem utility."""
    # Build parser, validate arguments, then run command.
    print(BANNER)
    parser = build_parser()

    try:
        # Parse args once, then execute the selected command path.
        app = FileSystemUtility(parser.parse_args())
        app.validate()
        app.run()
        return 0
    except KeyboardInterrupt:
        # Match common shell convention for Ctrl+C exit status.
        print(f"{C_RED}Interrupted by user{C_RESET}")
        return 130
    except RuntimeError as err:
        # Convert runtime failures into a clean user-facing error line.
        print(f"{C_RED}Error: {err}{C_RESET}")
        return 1
    finally:
        print(f"\n{C_GRAY}Done.{C_RESET}")


if __name__ == "__main__":
    # Convert main() return value into the process exit code for shell/CI use.
    raise SystemExit(main())
