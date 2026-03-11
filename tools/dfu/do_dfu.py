#!/usr/bin/python3

# Copyright (C) 2023 released Microchip Technology Inc.  All rights reserved.
# Microchip licenses to you the right to use, modify, copy and distribute
# Software only when embedded on a Microchip microcontroller or digital signal
# controller that is integrated into your product or third party product
# (pursuant to the sublicense terms in the accompanying license agreement).
# You should refer to the license agreement accompanying this Software for
# additional information regarding your rights and obligations.
# SOFTWARE AND DOCUMENTATION ARE PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF
# MERCHANTABILITY, TITLE, NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
# IN NO EVENT SHALL MICROCHIP OR ITS LICENSORS BE LIABLE OR OBLIGATED UNDER
# CONTRACT, NEGLIGENCE, STRICT LIABILITY, CONTRIBUTION, BREACH OF WARRANTY, OR
# OTHER LEGAL EQUITABLE THEORY ANY DIRECT OR INDIRECT DAMAGES OR EXPENSES
# INCLUDING BUT NOT LIMITED TO ANY INCIDENTAL, SPECIAL, INDIRECT, PUNITIVE OR
# CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA, COST OF PROCUREMENT OF
# SUBSTITUTE GOODS, TECHNOLOGY, SERVICES, OR ANY CLAIMS BY THIRD PARTIES
# (INCLUDING BUT NOT LIMITED TO ANY DEFENSE THEREOF), OR OTHER SIMILAR COSTS.

import argparse
import os
from dfu import DFU, Image


class RIO0:
    PE_VERSION = 1
    DEVICE_ID = "x9cxx053"

    ADDRESS_MAP = {
        "low": [0x60000000, 0x600F0000],
        "high": [0x600F0000, 0x601E0000],
        "file-system": [0x601E0000, 0x601EF000]
    }

    PAGE_SIZE = 4096
    SLOT_SIZE = 0xF0000

    @staticmethod
    def valid_device_id(device_id):
        if (device_id[0] == '2'
        and (device_id[3] == '6' or device_id[3] == '7')
        and device_id[1:3] == RIO0.DEVICE_ID[1:3]
        and device_id[5:8] == RIO0.DEVICE_ID[5:8]):
            return True
        elif (device_id[0] == '3'
        and int(device_id[3], 16) >= 8
        and device_id[1:3] == RIO0.DEVICE_ID[1:3]
        and device_id[5:8] == RIO0.DEVICE_ID[5:8]):
            return True

        return False


def main():
    parser = argparse.ArgumentParser(description='DFU tool')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-b", dest="bin_file", metavar=("Binary file", "Address|Section"), nargs=2,
                        help="Write option: Erase and write binary file to hexadecimal starting address or section (low, high, file-system).")
    group.add_argument("-e", dest="erase", metavar="Section", help="Erase option: Section to erase (low, high, file-system).")
    parser.add_argument("-s", dest="seq_num", help="Modifies image sequence number, can only be used for "
                                                   "a firmware image that occupies a single image slot size. "
                                                   "Example format: 0xffeeddcc", default=None)
    parser.add_argument("-p", "-port", dest="port", type=str, default="", help="User specific serial number of the FTDI "
                                                                               "port, else autodetect mechanism will be used.")
    parser.add_argument("-v", "-verbose", dest="verbose", action="store_true", default=False)

    args = parser.parse_args()

    if args.seq_num and not args.bin_file:
        print("ERROR: Sequence number argument should only be used in conjunction with binary file write option!")
        exit(1)

    dfu = DFU(RIO0, args.port, args.verbose)

    if args.erase:
        address = args.erase

        # Verify selected address region
        if address not in RIO0.ADDRESS_MAP:
            print(f"ERROR: Selected region '{address}' not in address map!")
            exit(1)

        high = RIO0.ADDRESS_MAP.get(address)[1]
        low = RIO0.ADDRESS_MAP.get(address)[0]

        address = low
        pages = int((high - low) / RIO0.PAGE_SIZE)

        print(f"Erasing {args.erase} region...")

        dfu.pe_erase(address, pages)

    if args.bin_file:
        bin_file = args.bin_file[0]
        address = args.bin_file[1]

        if not address.startswith("0x"):
            # Verify selected address region
            if address not in RIO0.ADDRESS_MAP:
                print(f"ERROR: Selected region '{address}' not in address map!")
                exit(1)

            address = RIO0.ADDRESS_MAP.get(address)[0]
        else:
            address = int(address, 0)

        if os.path.isfile(bin_file):
            with open(bin_file, 'rb') as file:
                bin_data = file.read()
        else:
            print(f"ERROR: {bin_file} does not exist!")
            exit(1)

        # Verify write doesn't start below the flash limit
        if address < RIO0.ADDRESS_MAP.get("low")[0]:
            print("ERROR: Attempting to write image starting below permissible DFU flash boundary!")
            exit(1)

        # Verify writing image doesn't exceed our upper flash limit
        if address+len(bin_data) > RIO0.ADDRESS_MAP.get("file-system")[1]:
            print("ERROR: Attempting to write image above permissible DFU flash boundary!")
            exit(1)

        # Set SEQ_NUM if requested
        if args.seq_num:
            if Image.is_firmware_image(RIO0, address, bin_data):
                if len(args.seq_num) != 10:
                    print("ERROR: Invalid sequence number provided! Please provide in format: 0xAABBCCDD (4 hex bytes)")
                    exit(1)
                args.seq_num = int(args.seq_num, 0)
            else:
                print(
                    "ERROR: User specified sequence number provided, please specify a single firmware image less than or equal "
                    "to image slot size!")
                exit(1)

        # Make image adjustments including FW_IMG_SRC_ADDR if necessary and working with a firmware image
        if Image.is_firmware_image(RIO0, address, bin_data):
            if args.verbose:
                print(f"Previous header: {bin_data.hex()[:512]}")

            image = Image(bin_data, args.seq_num, address)

            # Update bin_data to image byte stream
            bin_data = bytes(image.byte_stream)

            if args.verbose:
                print(f"Modified header: {bin_data.hex()[:512]}")

        print(f"Erasing binary file area: {hex(address)} - {hex(address + len(bin_data))}")

        dfu.pe_erase(address, ((len(bin_data) // RIO0.PAGE_SIZE) + (len(bin_data) % RIO0.PAGE_SIZE != 0)))

        print(f"Writing binary file: {bin_file} starting at: {hex(address)}...")

        dfu.pe_write(address, bin_data)

    print("Sending MCLR reset...")
    dfu.mclr_reset()

    print("Done!")


if __name__ == '__main__':
    main()
