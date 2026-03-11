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

import glob
import time
import os
import struct
import subprocess
import atexit

import ftd2xx
import serial


class Image:
    SEQ_NUM_OFFSET = 0x4
    FW_IMG_SRC_ADDR_OFFSET = 0x14
    COHERENCE_OFFSET = 0x08

    def __init__(self, byte_stream, seq_num, fw_img_src_adr):
        self.byte_stream = bytearray(byte_stream)
        self.fw_img_src_adr = fw_img_src_adr

        self.modify_fw_img_src_adr()

        if seq_num:
            self.seq_num = seq_num
            self.modify_sequence_number()

    def modify_sequence_number(self):
        previous_seq_num = struct.pack('>I', struct.unpack('<I', self.byte_stream[:4])[0])
        print(f"Previous sequence number: {previous_seq_num.hex()}")

        # Cast to unsigned long
        self.seq_num = struct.pack("<L", self.seq_num)
        # Modify sequence number
        self.byte_stream[:self.SEQ_NUM_OFFSET] = self.seq_num

        modified_seq_num = struct.pack('>I', struct.unpack('<I', self.seq_num)[0])
        print(f"Modified sequence number: {modified_seq_num.hex()}")

    def modify_fw_img_src_adr(self):
        previous_fw_img_src_adr = struct.pack('>I', struct.unpack('<I', self.byte_stream[self.FW_IMG_SRC_ADDR_OFFSET:self.FW_IMG_SRC_ADDR_OFFSET+4])[0])

        # Cast to unsigned long
        self.fw_img_src_adr = struct.pack("<L", self.fw_img_src_adr)
        modified_fw_img_src_adr = struct.pack('>I', struct.unpack('<I', self.fw_img_src_adr)[0])

        # Modify FW_IMG_SRC_ADR if required
        if previous_fw_img_src_adr != modified_fw_img_src_adr:
            print(f"Previous source address: {previous_fw_img_src_adr.hex()}")
            print(f"Modified source address: {modified_fw_img_src_adr.hex()}")

            self.byte_stream[self.FW_IMG_SRC_ADDR_OFFSET:self.FW_IMG_SRC_ADDR_OFFSET+4] = self.fw_img_src_adr

    @staticmethod
    def is_firmware_image(chip, address, bin_data):
        if ((address == chip.ADDRESS_MAP.get("low")[0] or address == chip.ADDRESS_MAP.get("high")[0])
                and (Image.check_coherence(bin_data) and len(bin_data) <= chip.SLOT_SIZE)):
            return True

        return False

    @staticmethod
    def check_coherence(bin_data):
        coherence_check_bytes = struct.pack('<I', struct.unpack('>I', "MCHP".encode())[0])
        coherence_bytes = bin_data[Image.COHERENCE_OFFSET:Image.COHERENCE_OFFSET+4]

        if coherence_bytes == coherence_check_bytes:
            return True

        return False


class FTDI:
    PIN_TX = 0x01   # Orange (TCK / PGC)
    PIN_RX = 0x02   # Yellow (TDI / PGD)
    PIN_CTS = 0x08  # Brown  (MCLR)
    PIN_BITMASK = PIN_TX | PIN_RX | PIN_CTS

    RESET_IO_BIT_MODE = 0x0
    ASYNC_BITBANG_MODE = 0x1

    DRIVER_DELAY = 0.5

    def __init__(self, device, debug=False):
        # ftd2xx object
        self.ftdi = ftd2xx.openEx(device)
        # FTDI serial number
        self.serial_number = self.ftdi.getDeviceInfo()['serial']
        # Debug status
        self.debug = debug

    def debug_print(self, msg):
        if self.debug:
            print(msg)

    @staticmethod
    def linux_load_vcp():
        subprocess.run(["sudo", "modprobe", "usbserial"], stderr=subprocess.DEVNULL, check=False)
        subprocess.run(["sudo", "modprobe", "ftdi_sio"], stderr=subprocess.DEVNULL, check=False)

        time.sleep(FTDI.DRIVER_DELAY)

    @staticmethod
    def linux_unload_vcp():
        subprocess.run(["sudo", "modprobe", "-r", "ftdi_sio"], stderr=subprocess.DEVNULL, check=False)
        subprocess.run(["sudo", "modprobe", "-r", "usbserial"], stderr=subprocess.DEVNULL, check=False)
        ports = glob.glob("/dev/ttyUSB*")
        if ports:
            print("Unable to unload VCP drivers, please ensure no device is open in another program")
            exit(1)

    @staticmethod
    def detect_devices(user_ftdi=""):
        try:
            devices = ftd2xx.listDevices()
        except ftd2xx.ftd2xx.DeviceError:
            devices = None

        if devices:
            # Only consider those with serial number (those without are likely in use - we can't get a handle)
            devices = list(filter(None, devices))

            # Select only the user selected FTDI device (if it exists)
            if user_ftdi:
                if user_ftdi.encode() in devices:
                    devices = [user_ftdi.encode()]
                else:
                    devices = None

        return devices

    def ftdi_write(self, data):
        return self.ftdi.write(bytes(data))

    def set_gpio_mode(self):
        self.ftdi.setBitMode(self.PIN_BITMASK, self.ASYNC_BITBANG_MODE)
        self.ftdi.setBaudRate(9600)

    def set_uart_mode(self):
        self.ftdi.write(chr(self.PIN_CTS))
        self.ftdi.setBitMode(self.PIN_TX | self.PIN_RX | self.PIN_CTS, 0)

    def pin_bitmask(self, index, pattern):
        mclr = int(pattern['mclr'][index])
        pgc = int(pattern['pgc'][index])
        pgd = int(pattern['pgd'][index])

        mask = (self.PIN_CTS if mclr == 1 else 0) | (self.PIN_TX if pgc == 1 else 0) | (self.PIN_RX if pgd == 1 else 0)

        return mask

    def send_pattern(self, pattern):
        self.debug_print("Sending pattern...")
        data = []

        for i in range(len(pattern.get('mclr'))):
            mask = self.pin_bitmask(i, pattern)
            data.append(mask)

        self.ftdi_write(data)
        self.debug_print("Pattern bitmask:")
        self.debug_print(data)

        time.sleep(DFU.PE_INIT_DELAY)

    def close(self):
        self.ftdi.close()


class DFU:
    RESET_PATTERN = {
        'mclr': "100000000000000000000000000000000000000000000000000000000000000001",
        'pgc':  "000000000000000000000000000000000000000000000000000000000000000000",
        'pgd':  "000000000000000000000000000000000000000000000000000000000000000000"
    }

    TEST_PATTERN = {
        'mclr': "111111111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001111",
        'pgc':  "000000000000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111000011110000111100001111111111111111",
        'pgd':  "000000000000000011111111000000000000000011111111111111110000000011111111000000001111111100000000000000000000000000000000111111111111111100000000111111110000000000000000111111110000000000000000000000000000000011111111000000001111111100000000000000000000000000000000000000000000"
    }

    # UART
    UART_BAUD = 230400
    UART_TIMEOUT = 1
    UART_ERASE_TIMEOUT = 30

    # PE commands
    PE_CMDS = {
        "PE_CMD_PAGE_ERASE": {"id": 0x05, "resp_len": 4},
        "PE_CMD_EXEC_VERSION": {"id": 0x07, "resp_len": 4},
        "PE_CMD_GET_DEVICE_ID": {"id": 0xA, "resp_len": 8},
        "PE_CMD_PGM_CLUSTER_VERIFY": {"id": 0x11, "resp_len": 4}
    }

    # PE misc
    PE_WRITE_CFG_METHOD = 0x1
    PE_INIT_DELAY = 0.5

    def __init__(self, chip, user_ftdi="", debug=False):
        self.chip = chip
        self.user_ftdi = user_ftdi
        self.uart = None
        self.debug = debug

        # Determine system
        if os.name == 'nt':
            self.os = 'nt'
        else:
            self.os = 'linux'

        if self.os == 'linux':
            # Unload VCP driver on Linux, so we can use D2XX driver
            FTDI.linux_unload_vcp()
            atexit.register(FTDI.linux_load_vcp)

        devices = FTDI.detect_devices(user_ftdi)

        if devices:
            for device in devices:
                try:
                    self.debug_print(f"Attempting to open FTDI device: {device.decode()}...")
                    self.ftdi = FTDI(device, debug)
                    self.debug_print(f"Successfully opened FTDI device: {device.decode()}")
                except ftd2xx.ftd2xx.DeviceError:
                    self.debug_print(f"Failed to open FTDI device: {device.decode()}")
                    continue

                self.ftdi.set_gpio_mode()
                self.ftdi.send_pattern(DFU.RESET_PATTERN)
                self.ftdi.send_pattern(DFU.TEST_PATTERN)
                self.ftdi.set_uart_mode()

                if self.os == 'linux':
                    self.ftdi.close()

                    # Load VCP driver
                    FTDI.linux_load_vcp()

                    ports = glob.glob("/dev/ttyUSB*")

                    if user_ftdi:
                        user_ftdi_identified = False
                        for port in ports:
                            proc = subprocess.run(["/bin/udevadm", "info", f"--name={port}"], check=False, capture_output=True)
                            if f"ID_SERIAL_SHORT={user_ftdi}" in proc.stdout.decode():
                                ports = [port]
                                user_ftdi_identified = True
                                break
                        
                        if not user_ftdi_identified:
                            ports = [] # Empty the ports list as we didn't find user specified device
                else:
                    ports = [f"COM{self.ftdi.ftdi.getComPortNumber()}"]

                    self.ftdi.close()

                for port in ports:
                    self.uart = serial.Serial(port, DFU.UART_BAUD, timeout=DFU.UART_TIMEOUT)
                    if self.os == 'linux':
                        proc = subprocess.run(["/bin/udevadm", "info", f"--name={port}"], check=False, capture_output=True)
                        if f"DEVNAME={port}" not in proc.stdout.decode() or f"ID_SERIAL_SHORT={device.decode()}" not in proc.stdout.decode():
                            continue

                    time.sleep(0.1)

                    pe_version = self.get_pe_version()
                    if pe_version == chip.PE_VERSION:
                        device_id = self.get_device_id()

                        if chip.valid_device_id(device_id):
                            print(f"Entered DFU mode with FTDI device: {device.decode()} ({self.uart.port})")
                            atexit.unregister(FTDI.linux_load_vcp)
                            return

                        print(f"Device ID: {device_id} did not match expected device ID: {chip.DEVICE_ID}")
                if self.uart:
                    self.uart.close()

                if self.os == "linux":
                    FTDI.linux_unload_vcp()

            if user_ftdi:
                print(f"Failed to find PE version response using specified FTDI cable: {user_ftdi}")
            else:
                print(f"Failed to find PE version response using available FTDI cables: {[device.decode() for device in devices]}")
        else:
            if user_ftdi:
                print("Failed to find user specified FTDI device")
            else:
                print("Failed to find any available FTDI devices")

        print("Please ensure FTDI cable is not in use by another program handle and the FTDI D2XX direct driver is "
              "installed correctly!")
        if self.os == "linux":
            print("Also ensure you have correct permissions for accessing the required port.")

        exit(1)

    def debug_print(self, msg):
        if self.debug:
            print(msg)

    def get_pe_version(self):
        self.debug_print("get_pe_version")

        cmd = self.PE_CMDS.get("PE_CMD_EXEC_VERSION")

        # Assemble PE version command
        data = cmd.get("id") << 16
        data |= 0x1
        data = struct.pack('<I', data)

        # Write PE version command
        self.uart_write(data)

        # Read response
        resp = self.pe_read_response(cmd)

        if len(resp) == 4 and resp[2] == cmd.get("id"):
            pe_version = resp[0]
            return pe_version

        return None

    def get_device_id(self):
        self.debug_print("get_device_id")

        cmd = self.PE_CMDS.get("PE_CMD_GET_DEVICE_ID")

        # Assemble device ID command
        data = cmd.get("id") << 16
        data |= 0x1
        data = struct.pack('<I', data)

        # Write device ID command
        self.uart_write(data)

        # Read response
        resp = self.pe_read_response(cmd)

        device_id = bytearray(struct.pack(">Q", int.from_bytes(resp, byteorder='little'))).hex()[:cmd.get("resp_len")]

        self.debug_print(f"device ID: {device_id}")

        return device_id

    def pe_erase(self, address, pages):
        write_buffer = bytearray()

        self.debug_print("pe_erase")

        self.debug_print(f"address: {hex(address)}")
        self.debug_print(f"pages: {pages}")

        cmd = self.PE_CMDS.get("PE_CMD_PAGE_ERASE")

        # Assemble erase command
        data = pages & 0x0000ffff
        data |= cmd.get("id") << 16
        write_buffer.extend(struct.pack('<I', data))

        # Address
        write_buffer.extend(struct.pack('<I', address))

        self.uart_write(write_buffer)

        # Read response
        # Increase timeout for erase operation
        self.uart.timeout = self.UART_ERASE_TIMEOUT
        resp = self.pe_read_response(cmd)
        self.uart.timeout = self.UART_TIMEOUT

        if len(resp) != 4 or resp[2] != cmd.get("id") or resp[0] != 0 or resp[1] != 0:
            print("Erase failed!")
            exit(1)

        print("Erase success")

    def pe_write(self, address, bin_data):
        self.debug_print("pe_write")

        self.debug_print(f"address: {hex(address)}")
        self.debug_print(f"length: {hex(len(bin_data))}")

        n = ((len(bin_data) // self.chip.PAGE_SIZE) + (len(bin_data) % self.chip.PAGE_SIZE != 0))
        r = len(bin_data) % self.chip.PAGE_SIZE

        self.debug_print(f"n: {n} r: {r}")

        for i in range(n):
            write_buffer = bytearray()

            print(f"Write status: {i + 1}/{n}")

            cmd = self.PE_CMDS.get("PE_CMD_PGM_CLUSTER_VERIFY")

            # Assemble write command
            data = 0
            data |= (0x0000ffff & cmd.get("id")) << 16
            data |= (self.PE_WRITE_CFG_METHOD & 0x0000ffff)
            write_buffer.extend(struct.pack('<I', data))

            # Assemble address
            offset = address + (self.chip.PAGE_SIZE * i)
            self.debug_print(f"Address: {hex(offset)}")
            write_buffer.extend(struct.pack('<I', offset))

            # Update length to remainder if the last iteration doesn't contain a 4096 chunk
            if (i == (n - 1)) and (r > 0):
                length = r
            else:
                length = self.chip.PAGE_SIZE

            # Assemble length
            self.debug_print(f"Length: {hex(length)}")
            write_buffer.extend(struct.pack('<I', length))

            chunk = bin_data[(self.chip.PAGE_SIZE * i):((self.chip.PAGE_SIZE * i) + length)]

            # Assemble Checksum
            checksum = 0
            for byte_index in range(length):
                checksum += chunk[byte_index]

            self.debug_print(f"Checksum: {checksum}")
            write_buffer.extend(struct.pack('<I', checksum))

            # Data
            self.debug_print("Data:")
            write_buffer.extend(chunk)

            self.uart_write(write_buffer)

            # Response
            resp = self.pe_read_response(cmd)
            if len(resp) != 4 or resp[2] != cmd.get("id") or resp[0] != 0 or resp[1] != 0:
                print("Write failed!")
                exit(1)

            self.debug_print("Write success")

        print("Writing finished")

    def mclr_reset(self):
        self.uart.close()

        # We must unload the VCP before we use D2XX driver
        if self.os == "linux":
            FTDI.linux_unload_vcp()

        ftdi = FTDI(self.ftdi.serial_number, self.debug)
        ftdi.set_gpio_mode()
        ftdi.send_pattern(self.RESET_PATTERN)
        ftdi.set_uart_mode()
        ftdi.close()

        # Load back the VCP driver
        if self.os == "linux":
            FTDI.linux_load_vcp()

    def pe_read_response(self, cmd):
        # Reads response until UART timeout hit
        resp = self.uart.read(cmd.get("resp_len"))

        self.debug_print(f"<= {resp.hex()}")

        return resp

    def uart_write(self, data):
        self.uart.write(data)
        self.debug_print(f"=> {data.hex()}")
