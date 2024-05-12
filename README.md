# QE - quick Qemu command shorterner and VM launcher

## Examples

Run virtual machine image file from CLI. Just like this:
```bash
qe w11.vhd
```

The same for live iso:
```bash
qe Fedora-KDE-Live-x86_64-40-1.14.iso
```

Quickly create an image and start VM installation from iso with just a single command:
```bash
qe ubuntu.qcow2 ~/Downloads/ubuntu-24.04-beta-desktop-amd64.iso
```

Generate Qemu command for manual editing later, with `-n` option:
```bash
qe windows-server-2022.vdi -n
```
`qemu-system-x86_64 -enable-kvm -smp 2 -m 4G -bios /usr/share/ovmf/x64/OVMF.fd -drive file=windows-server-2022.qcow2,format=qcow2,index=0,media=disk -display sdl`

Avoid changing VM file with `-s` (`--snapshot`) option and do all your crazy experiments!
```bash
qe arch.qcow2 -s
```

## Features

- Defaults for CPU and memory. You can still use `-m` or `-smp` to specify your own
- Automatic image type recognition (including something like *.iso or /dev/sda)
- Uses UEFI by default if OVMF.fd is found in the list of usual locations.
- Accepts `qemu-system-x86_64` arguments, like `-snapshot`.
- Can create and pass folders or files to VM with the help of `mkisoifs` command (should be installed on your system).
- Use it with the `-n` flag to generate and print a qemu command for manual editing.
- Requires no dependencies other than plain python3 for main functionality (you still have to install Qemu, as it is a Qemu launcher).
- Currently supports GNU Linux only. It worked on Windows, but the focus is on GNU Linux. MacOS commands not implemented but planned.

## Installation

Download [qe](./qe) and place it to your PATH

## Usage

```
Usage: qe [images] (script options) (other qemu params)

Wrapper for qemu to simplify VM launching from command line
It provides automatic image type detection, enables UEFI and acceleration if possible and provides some additional niceties, see below

Script options:

-p             forward ssh and http ports
-i --make-iso  Makes and mounts ISO from folder of file
-l --no-efi    run without UEFI (default tries to find OVMF.fd)
-s --snapshot  Run VM in without saving any changes
-n             generate command and print without running

-u             select USB device (not implemented yet, TODO)
-f             FAT folder, read only (not implemented yet, TODO)

--help         display help message

You can also use all available qemu-system-x86_64 parameters
```

## TODO

- [x] image creation if not exists
- [x] config in json
- [x] -display sdl if windows image
- [ ] fat folders
- [ ] usb device selection and passthrough
- [ ] move all handles to argparse instead of sys.argv
- [ ] MacOS support
- [ ] installation oneliner
- [ ] flexible port forwarding but keeping the defaults
- [ ] ?? packaging
- [ ] download OVMF.fd if not present
