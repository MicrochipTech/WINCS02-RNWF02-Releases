import sys
import os
import getopt
import struct
import json
import base64
import socket
import re
import math

from pyclibrary import CParser
from pprint import pprint
from datetime import datetime, timezone

usage = """usage:
  cfgc.py [-H <header>] -i <infile> | --in=<infile> [-o <outfile> | --out=<outfile>] [-c | --compile] -e | --encode
  cfgc.py [-H <header>] -i <infile> | --in=<infile> [-o <outfile> | --out=<outfile>] -d | --decode
  cfgc.py -h | --help

Options:
  -h | --help                       Show this information.
  -H <header> | --header=<header>   Interface header file path.
  -i <infile> | --in=<infile>       Input file.
  -o <outfile> | --out=<outfile>    Output file.
  -c | --compile                    Compile AT commands to JSON representation.
  -e | --encode                     Encode JSON representation to binary format.
  -d | --decode                     Decode binary format to JSON representation.

"""

# Default interface header: WINCS02 nc_driver header relative to this script's location.
DEFAULT_HEADER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '..', '..', 'WINCS02', 'driver', 'src', 'include',
                              'microchip_wincs02_intf.h')

if __name__ == "__main__":
    try:
        opts, remaining = getopt.getopt(sys.argv[1:], 'hH:i:o:edc', ['help', 'header=', 'in=','out=','encode','decode','compile'])
    except getopt.GetoptError:
        sys.exit(1)

    cfg_in           = None
    cfg_out          = None
    cfg_in_fh        = None
    cfg_out_fh       = None
    encode           = False
    cfg_in_mode      = ''
    decode           = False
    cfg_out_mode     = ''
    cfg_out_encoding = None
    compile          = False
    src_in           = None
    src_out          = None
    src_in_fh        = None
    src_in_json      = None
    src_out_fh       = None
    src_out_mode     = None
    header_path      = DEFAULT_HEADER

    print('RNWF Configuration Command Compiler/Encoder/Decoder (c) 2025 Microchip Technology Inc')
    print()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(usage)
        elif opt in ('-H', '--header'):
            header_path = os.path.normpath(arg)
        elif opt in ('-i', '--in'):
            cfg_in = os.path.normpath(arg)
            src_in = cfg_in
        elif opt in ('-o', '--out'):
            cfg_out = os.path.normpath(arg)
            src_out = cfg_out
        elif opt in ('-e', '--encode'):
            encode           = True
            cfg_in_mode      = 'r'
            cfg_out_mode     = 'wb'
            cfg_out_encoding = None
        elif opt in ('-d', '--decode'):
            decode           = True
            cfg_in_mode      = 'rb'
            cfg_out_mode     = 'w'
            cfg_out_encoding = 'utf8'
        elif opt in ('-c', '--compile'):
            compile          = True
            src_in_mode      = 'r'
            src_out_mode     = 'w'

    if not encode and not decode and not compile:
        exit(0)

    if compile:
        cfg_in = None
    else:
        src_in = None

    header_path = os.path.normpath(header_path)
    print('parsing interface header %s' %(header_path))
    parser = CParser(header_path)

    print('building tables...')
    all_macros   = parser.defs['macros']
    all_modules  = {parser.eval(val): key for key, val in all_macros.items() if key.startswith('WINC_MOD_ID_')}
    all_commands = {parser.eval(val): key for key, val in all_macros.items() if key.startswith('WINC_CMD_ID_')}

    all_values   = parser.defs['values']
    all_types    = {val: key for key, val in all_values.items() if key.startswith('WINC_TYPE')}

    if compile and src_in:
        print('opening source file %s' %(src_in))
        src_in_fh = open(src_in, src_in_mode)
    elif cfg_in:
        print('opening configuration file %s' %(cfg_in))
        cfg_in_fh = open(cfg_in, cfg_in_mode)

    if cfg_out_mode:
        if cfg_out:
            print('opening output file %s' %(cfg_out))
            cfg_out_fh = open(cfg_out, cfg_out_mode, encoding=cfg_out_encoding)
        else:
            print('outputting to terminal')
            cfg_out_fh = sys.stdout
    elif src_out_mode:
        if src_out:
            src_out_fh = open(src_out, src_out_mode)
            print('opening output file %s' %(src_out))
        else:
            src_out_fh = sys.stdout
            print('outputting to terminal')

    F_CFG_ARC_HDR      = 'bbHI'
    F_CFG_ARC_ELEM_HDR = 'HHbb'
    F_CFG_TLV_ELEM     = '>bbH'

    if decode and cfg_in_fh:
        print('decoding %s' %(cfg_in))
        cfg_arc_file_header = cfg_in_fh.read(struct.calcsize(F_CFG_ARC_HDR))

        if cfg_arc_file_header:
            cfg_arc_hdr = dict(zip(['sig', 'hdr_len', 'pad', 'time'], struct.unpack(F_CFG_ARC_HDR, cfg_arc_file_header)))

            cfg_cmds = []

            while True:
                elem_file_hdr = cfg_in_fh.read(struct.calcsize(F_CFG_ARC_ELEM_HDR))

                if not elem_file_hdr:
                    break

                elem_list_hdr  = dict(zip(['id', 'data_length', 'num_elements', 'pad'], struct.unpack(F_CFG_ARC_ELEM_HDR, elem_file_hdr)))
                elem_list_data = cfg_in_fh.read(elem_list_hdr['data_length'])

                if not elem_list_data:
                    break

                elems = []

                for i in range(elem_list_hdr['num_elements']):
                    elem_hdr  = dict(zip(['type', 'flags', 'length'], struct.unpack(F_CFG_TLV_ELEM, elem_list_data[0:struct.calcsize(F_CFG_TLV_ELEM)])))

                    elem_list_data = elem_list_data[struct.calcsize(F_CFG_TLV_ELEM):]
                    elem_data = elem_list_data[0:elem_hdr['length']]
                    elem_list_data = elem_list_data[elem_hdr['length']:]

                    elem = {}

                    elem['type']   = all_types[elem_hdr['type']]
                    elem['length'] = len(elem_data)

                    if elem['type'] == 'WINC_TYPE_INTEGER':
                        elem['value'] = int.from_bytes(elem_data, byteorder='big', signed=True)
                    elif elem['type'] == 'WINC_TYPE_INTEGER_UNSIGNED':
                        elem['value'] = int.from_bytes(elem_data, byteorder='big', signed=False)
                    elif elem['type'] == 'WINC_TYPE_INTEGER_FRAC':
                        frac = dict(zip(['i', 'f'], struct.unpack('>HH', elem_data)))
                        elem['value'] = float('%d.%d' %(frac['i'],frac['f']))
                    elif elem['type'] == 'WINC_TYPE_STRING':
                        test_str = ''
                        for s in elem_data.decode('utf-8'):
                            if s.isprintable():
                                test_str += s
                            elif s in '\t\\\"\r\n\a\b\v\f\x1b':
                                test_str += s
                            else:
                                test_str = None
                                break
                        if test_str:
                            elem['value'] = test_str
                            elem['encoding'] = 'ascii'
                        else:
                            elem['value'] = elem_data.hex()
                            elem['encoding'] = 'bytes'
                    elif elem['type'] == 'WINC_TYPE_BYTE_ARRAY':
                        elem['value'] = elem_data.hex()
                        elem['encoding'] = 'bytes'
                    elif elem['type'] == 'WINC_TYPE_BOOL':
                        elem['value'] = ord(elem_data) != 0
                    elif elem['type'] == 'WINC_TYPE_IPV4ADDR':
                        elem['value'] = socket.inet_ntop(socket.AF_INET, elem_data[0:4])

                        if elem['length'] == 5:
                            elem['scope'] = elem_data[4]
                        elif elem['length'] == 8:
                            elem['scope'] = socket.inet_ntop(socket.AF_INET, elem_data[4:8])
                    elif elem['type'] == 'WINC_TYPE_IPV6ADDR':
                        elem['value'] = socket.inet_ntop(socket.AF_INET6, elem_data[0:16])

                        if elem['length'] == 17:
                            elem['scope'] = elem_data[16]
                    elif elem['type'] == 'WINC_TYPE_MACADDR':
                        elem['length'] = 6
                        elem['value'] = elem_data[:6].hex(':')
                    elif elem['type'] == 'WINC_TYPE_UTC_TIME':
                        elem['value'] = int.from_bytes(elem_data, byteorder='big', signed=False)
                    else:
                        elem['value'] = elem_data

                    elems.append(elem)

                cfg_cmds.append({'cmd':all_commands[elem_list_hdr['id']], 'elems':elems})

            if cfg_out_fh:
                print('outputting decoded configuration')
                print(json.dumps(cfg_cmds, indent=4), file=cfg_out_fh)

    elif compile and src_in:
        print('compiling %s' %(src_in))
        cfg_cmds = []

        for line in src_in_fh:
            line = line.rstrip()

            if line.endswith('*/'):
                m = re.search('^AT\+(\w+)=(.+)\s+/\*\s*(.*)\s*\*/$', line)
            else:
                m = re.search('^AT\+(\w+)=(.+)$', line)

            if m:
                command    = m.group(1)
                parameters = m.group(2).rstrip()
                comment    = None

                if len(m.groups()) == 3:
                    comment = m.group(3).rstrip()

                if 'WINC_CMD_ID_'+command in all_commands.values():
                    elems = []
                    param_list = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', parameters)

                    for param in param_list:
                        elem = {}

                        if param.startswith('"'):
                            param = param.strip('"')

                            try:
                                if '/' in param:
                                    (ip, scope) = param.split('/')
                                else:
                                    ip    = param
                                    scope = None
                                ipv4 = socket.inet_pton(socket.AF_INET, ip)
                                if scope:
                                    try:
                                        socket.inet_pton(socket.AF_INET, scope)
                                        elem['length'] = 8
                                    except:
                                        scope = int(scope)
                                        elem['length'] = 5
                                else:
                                    elem['length'] = 4
                            except:
                                try:
                                    if '/' in param:
                                        (ip, scope) = param.split('/')
                                    else:
                                        ip    = param
                                        scope = None

                                    ipv6  = socket.inet_pton(socket.AF_INET6, ip)
                                    if scope:
                                        scope = int(scope)
                                except:
                                    if re.search('^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$', param):
                                        elem['type']     = 'WINC_TYPE_MACADDR'
                                        elem['value']    = param
                                        elem['length']   = 6
                                    elif re.search('^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$', param):
                                        elem['type']     = 'WINC_TYPE_UTC_TIME'
                                        elem['value']    = int((datetime.strptime(param, '%Y-%m-%dT%H:%M:%S.%fZ') - datetime(1970, 1, 1)).total_seconds())
                                        elem['length']   = 4
                                    else:
                                        elem['type']     = 'WINC_TYPE_STRING'
                                        elem['value']    = ''
                                        escape = False
                                        for s in param:
                                            if escape == True:
                                                escape_char = {'t':0x09, '\\':0x5c, '"':0x22, 'r':0x0d, 'n':0x0a, 'a':0x07, 'b':0x08, 'v':0x0b, 'f':0x0c, 'e':0x1b}
                                                elem['value'] += chr(escape_char[s])
                                                escape = False
                                            elif s == '\\':
                                                escape = True
                                            else:
                                                elem['value'] += s

                                        elem['length']   = len(elem['value'])
                                        elem['encoding'] = 'ascii'
                                else:
                                    elem['type']   = 'WINC_TYPE_IPV6ADDR'
                                    elem['value']  = ip
                                    if scope:
                                        elem['length'] = 17
                                        elem['scope'] = scope
                                    else:
                                        elem['length'] = 16
                            else:
                                elem['type']   = 'WINC_TYPE_IPV4ADDR'
                                elem['value']  = ip
                                if scope:
                                    elem['scope'] = scope
                        elif param.startswith('['):
                            elem['type']     = 'WINC_TYPE_BYTE_ARRAY'
                            elem['value']    = param.strip('[]')
                            elem['length']   = int(len(elem['value'])/2)
                            elem['encoding'] = 'bytes'
                        elif param.startswith('0x'):
                            elem['type']     = 'WINC_TYPE_INTEGER_UNSIGNED'
                            elem['value']    = int(param, 16)
                            elem['length']   = int((math.ceil(math.log(elem['value'], 2))+7)/8)
                        elif param.startswith('0o'):
                            elem['type']     = 'WINC_TYPE_INTEGER_UNSIGNED'
                            elem['value']    = int(param, 8)
                            elem['length']   = int((math.ceil(math.log(elem['value'], 2))+7)/8)
                        elif param.startswith('0b'):
                            elem['type']     = 'WINC_TYPE_INTEGER_UNSIGNED'
                            elem['value']    = int(param, 2)
                            elem['length']   = int((math.ceil(math.log(elem['value'], 2))+7)/8)
                        elif param == 'TRUE' or param == 'FALSE':
                            elem['type']     = 'WINC_TYPE_BOOL'
                            elem['value']    = (param == 'TRUE')
                            elem['length']   = 1
                        elif param.lstrip('-').isdigit():
                            elem['value']    = int(param)
                            if elem['value'] < 0:
                                elem['type']   = 'WINC_TYPE_INTEGER'
                                elem['length'] = 4
                            else:
                                elem['type']   = 'WINC_TYPE_INTEGER_UNSIGNED'
                                elem['length'] = int((math.ceil(math.log(elem['value'], 2))+7)/8)
                        else:
                            elem['type']     = 'WINC_TYPE_INTEGER_FRAC'
                            elem['value']    = float(param)
                            elem['length']   = 4

                        elems.append(elem)

                    cfg_cmds.append({'at':'AT'+command+'='+parameters, 'comment':comment, 'cmd':'WINC_CMD_ID_'+command, 'elems':elems})
                else:
                    print('error, command \'%s\' not recognised' %(m.group(1)))

        def del_nulls(value):
            if isinstance(value, dict):
                return {k: del_nulls(v) for k, v in value.items() if v is not None}
            elif isinstance(value, list):
                return [del_nulls(item) for item in value if item is not None]
            else:
                return value

        cfg_cmds = del_nulls(cfg_cmds)

        src_in_json = json.dumps(cfg_cmds, indent=4)

        if not encode:
            print(src_in_json, file=src_out_fh)

    if encode:
        cfg_in_json = None

        if cfg_in_fh:
            print('encoding %s' %(cfg_in))
            cfg_in_json = json.load(cfg_in_fh)
        elif src_in_json:
            print('encoding JSON')
            cfg_in_json = json.loads(src_in_json)

        cfg_out_fh.write(struct.pack(F_CFG_ARC_HDR, 0, struct.calcsize(F_CFG_ARC_HDR), 0, int(datetime.now(timezone.utc).timestamp())))

        for cfg_cmd in cfg_in_json:
            id = parser.eval(all_macros[cfg_cmd['cmd']])

            elem_data_length = 0
            elem_data = b''
            for elem in cfg_cmd['elems']:

                elem_data += struct.pack(F_CFG_TLV_ELEM, all_values[elem['type']], 0, elem['length'])

                if elem['type'] == 'WINC_TYPE_INTEGER':
                    elem_data += elem['value'].to_bytes(elem['length'], byteorder='big', signed=True)
                elif elem['type'] == 'WINC_TYPE_INTEGER_UNSIGNED':
                    elem_data += elem['value'].to_bytes(elem['length'], byteorder='big')
                elif elem['type'] == 'WINC_TYPE_INTEGER_FRAC':
                    (i, f) = str(elem['value']).split('.')
                    elem_data += int(i).to_bytes(2, byteorder='big', signed=True)
                    elem_data += int(f).to_bytes(2, byteorder='big')
                elif elem['type'] == 'WINC_TYPE_STRING':
                    if elem['encoding'] == 'bytes':
                        elem_data += bytes.fromhex(elem['value'].replace(':', ''))
                    elif elem['encoding'] == 'ascii':
                        elem_data += elem['value'].encode('utf-8')
                    else:
                        pass
                elif elem['type'] == 'WINC_TYPE_BYTE_ARRAY':
                    elem_data += bytes.fromhex(elem['value'])
                elif elem['type'] == 'WINC_TYPE_BOOL':
                    elem_data += bytes((elem['value'],))
                elif elem['type'] == 'WINC_TYPE_IPV4ADDR':
                    elem_data += socket.inet_pton(socket.AF_INET, elem['value']);

                    if 'scope' in elem:
                        if isinstance(elem['scope'], int):
                            elem_data += elem['scope'].to_bytes(1, byteorder='big')
                        elif isinstance(elem['scope'], str):
                            elem_data += socket.inet_pton(socket.AF_INET, elem['scope']);
                elif elem['type'] == 'WINC_TYPE_IPV6ADDR':
                    elem_data += socket.inet_pton(socket.AF_INET6, elem['value']);
                    if 'scope' in elem:
                        elem_data += elem['scope'].to_bytes(1, byteorder='big')
                elif elem['type'] == 'WINC_TYPE_BOOL':
                    if elem['value']:
                        elem_data += 1
                    else:
                        elem_data += 0
                elif elem['type'] == 'WINC_TYPE_MACADDR':
                    elem_data += bytes.fromhex(elem['value'].replace(':', ''))
                elif elem['type'] == 'WINC_TYPE_UTC_TIME':
                    elem_data += elem['value'].to_bytes(elem['length'], byteorder='big')
                else:
                    pass

                if elem_data:
                    elem_data_length += struct.calcsize(F_CFG_TLV_ELEM) + elem['length']

            cfg_out_fh.write(struct.pack(F_CFG_ARC_ELEM_HDR, id, elem_data_length, len(cfg_cmd['elems']), 0))
            cfg_out_fh.write(elem_data)

        print('encoding complete, data written to %s' %(cfg_out))

    if cfg_in_fh:
        cfg_in_fh.close()

    if cfg_out_fh:
        cfg_out_fh.close()
