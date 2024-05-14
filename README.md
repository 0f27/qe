# QE - quick Qemu command shorterner and VM launcher

## Examples

Run virtual machine image file from CLI. Just like this:
```bash
qe w11.vmdk
```

The same for live iso:
```bash
qe Fedora-KDE-Live-x86_64-40-1.14.iso
```

Quickly create an image and start VM installation from iso with just a single command:
```bash
# ubuntu.qcow2 will be created with default size if not exists
qe ubuntu.qcow2 ~/Downloads/ubuntu-24.04-beta-desktop-amd64.iso
```

Generate Qemu command to save or edit later, with `-n` option:
```bash
qe windows-server-2022.vhd -n
# qemu-system-x86_64 -enable-kvm -smp 2 -m 4G -bios /usr/share/ovmf/x64/OVMF.fd -drive file=windows-server-2022.vpc,format=qcow2,index=0,media=disk -display sdl
```

Avoid changing VM file with `-s` (`--snapshot`) option and do all your crazy experiments!
```bash
qe arch.qcow2 -s
```

Use `qemu-system-x86_64` arguments as well as script's own:
```bash
qe kali.qcow2 -s -net none
```

Pack your file or folder to iso and mount with image:
```bash
# ./volatility3.iso will be created with folder contents and mounted
qe Fedora-KDE-Live-x86_64-40-1.14.iso -i ./volatility3
```

## Installation

Pre-requisites Fedora:
```bash
sudo dnf install -y \
    edk2-ovmf \
    qemu-{kvm,tools} \
    genisoimage
```

Pre-requisites Arch:
```bash
sudo pacman -Sy --noconfirm \
    qemu-desktop \
    cdrkit
```

Pre-requisites Ubuntu:
```bash
sudo apt install -y \
    qemu-kvm \
    genisoimage
```

Pre-requisites Debian:
```bash
sudo apt update
sudo apt install -y \
    qemu-{user,system{,-gui},utils} \
    genisoimage
```

Then just download [qe](./qe) and place it to your PATH:
```bash
wget https://raw.githubusercontent.com/XelorR/qe/main/LICENSE -O - | less
mkdir -p ~/.local/bin
# assuming that ~/.local/bin is in your PATH
# if not, just modify your .bashrc, .zshrc or .config/fish/config.fish accordingly
wget https://raw.githubusercontent.com/XelorR/qe/main/qe -O ~/.local/bin/qe
chmod +x ~/.local/bin/qe
```

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
- [x] installation oneliner
- [ ] flexible port forwarding but keeping the defaults
- [ ] ?? packaging
- [ ] download OVMF.fd if not present
- [ ] ova files unpack and alias to vmdk
- [ ] config.json documentation
- [ ] support for multiple iso creation
