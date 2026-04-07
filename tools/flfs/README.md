# Flash File System (FLFS) Tool

The FLFS tool creates and manages flash file system images for WINCS02 and
RNWF02 modules. Use it to provision custom TLS certificates, private keys,
and configuration files.

## What This Folder Contains

- `flfs.exe`: FLFS utility for Windows
- `flfs`: FLFS utility for Linux
- `certs/ssl.tar`: default SSL certificate archive

## Usage

To create a file system image, use the following command:

**Windows:**

```
flfs.exe -s 61440 -b 0x601e0000 -c -a certs\ssl.tar -i flfs_image.bin -m "certs/:1" -m "private/:2"
```

**Linux:**

```
./flfs -s 61440 -b 0x601e0000 -c -a certs/ssl.tar -i flfs_image.bin -m "certs/:1" -m "private/:2"
```

This will create a file system image with SSL certificates and private keys.

## Adding Configuration Files

Use the `-f` flag to include individual files such as binary configuration
files produced by the [cfgc](../cfgc/) tool:

```
flfs.exe -s 61440 -b 0x601e0000 -c -a certs\ssl.tar -f config.bin -i flfs_image.bin -m "certs/:1" -m "private/:2"
```

## Custom Certificates

The default `certs/ssl.tar` contains the pre-packaged TLS root certificates
listed in the release notes. To add your own certificates, create a custom
tar archive and rebuild the file system image.

## Output

The tool produces a `flfs_image.bin` that can be flashed to the module's
file system partition.

## Help

Run `flfs.exe -h` (or `./flfs -h` on Linux) to see all available options.
