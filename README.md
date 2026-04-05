# QE - powerful and easy to use command line virtual machine launcher based on Qemu

> I use it myself, so expect minor bugs and hidden features.
> If you find something, feel free to open issue or create pull request.

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
# qemu-system-x86_64 -enable-kvm -smp 2 -m 4G -bios /usr/share/ovmf/x64/OVMF.fd -drive file=windows-server-2022.vhd,format=vpc,index=0,media=disk -display sdl
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

Run your HDD/SSD/NVME as a virtual machine!
```bash
qe /dev/sda --snapshot
```

UEFI is the default! But you can run in legacy mode too:
```bash
qe MX.qcow2 --no-efi
```

Create and run [Ventoy](https://ventoy.net/en/index.html) [vtoyboot](https://ventoy.net/en/plugin_vtoyboot.html) and [vhdboot](https://ventoy.net/en/plugin_vhdboot.html) images to launch from your USB:
```bash
# UEFI and fixed image size as you need for Ventoy
qe w11.vhd.vtoy Win11_23H2_English_x64v2.iso -i ./drivers_and_software
mv w11.vhd.vtoy w11.vhd
```

## Installation

```bash
#!/usr/bin/env bash

. /etc/os-release

# installing pre-requisites
if [[ "$ID" == "ubuntu" ]]; then
  sudo apt install -y \
    wget \
    qemu-kvm \
    genisoimage
elif [ "$ID" = "debian" ]; then
  sudo apt update
  sudo apt install -y \
    wget \
    qemu-{user,system{,-gui},utils} \
    genisoimage
elif [ "$ID" = "fedora" ]; then
  sudo dnf install -y \
    wget \
    edk2-ovmf \
    qemu-{kvm,tools} \
    genisoimage
elif [ "$ID_LIKE" = "arch" ]; then
  sudo pacman -Sy --noconfirm \
    wget \
    qemu-desktop \
    cdrkit
fi

# copying script itself
mkdir -p ~/.local/bin
wget https://raw.githubusercontent.com/0f27/qe/main/qe -O ~/.local/bin/qe
chmod +x ~/.local/bin/qe
```

## Usage

Run `qe --help` for full usage information.

```bash
qe [images] [options]
```

**Quick examples:**

```bash
# Run an existing VM
qe ubuntu.qcow2

# Create and run a new VM with specific size
qe new.qcow2 --size 20G

# Run a live ISO with console only (no GUI)
qe Fedora-Live.iso -c

# Run with snapshot mode (changes not saved)
qe windows.qcow2 -s

# Mount a folder as ISO
qe vm.qcow2 -i ./drivers

# Forward custom port (host:guest)
qe vm.qcow2 --port 8080:80

# Use default ports (-p) plus custom port
qe vm.qcow2 -p --port 3306:3306

# Mount folder as FAT drive (read-only)
qe vm.qcow2 -f ./shared

# Mount folder as FAT drive (read-write)
qe vm.qcow2 -f ./shared:rw

# Mount multiple folders
qe vm.qcow2 -f ./drivers -f ./shared:rw

# Print QEMU command without running
qe image.qcow2 -n
```

## Configuration

QE looks for a configuration file at `~/.config/qe/config.json`. This file is created automatically with default values if it doesn't exist.

### Default Configuration

```json
{
  "memory": "3G",
  "cpu_cores": "2",
  "image_size_to_create": "40G",
  "ports_passthrough": {
    "22": 9922,
    "80": 9980,
    "443": 9943,
    "21": 9921,
    "3389": 9989
  }
}
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `memory` | string | Default memory allocation for VMs (e.g., "4G", "2048M") |
| `cpu_cores` | string | Number of CPU cores to allocate |
| `image_size_to_create` | string | Default size for new disk images |
| `ports_passthrough` | object | Port forwarding mappings (guest_port: host_port) |

### Example Custom Configuration

```json
{
  "memory": "8G",
  "cpu_cores": "4",
  "image_size_to_create": "100G",
  "ports_passthrough": {
    "22": 9922,
    "80": 9980,
    "8080": 8080
  }
}
```

## TODO

- [x] image creation if not exists
- [x] config in json
- [x] -display sdl if windows image
- [x] fat folders
- [ ] usb device selection and passthrough
- [x] move all handles to argparse instead of sys.argv
- [ ] MacOS support
- [x] installation oneliner
- [x] flexible port forwarding but keeping the defaults
- [ ] ?? packaging
- [x] download OVMF.fd if not present
- [x] ova files unpack and alias to vmdk
- [ ] config.json documentation
- [ ] support for multiple iso creation
- [x] refactor
- [ ] tests!
- [ ] add network setup to connect several VM instances
- [x] beautify --help
- [x] add flag for fixed size images
- [x] add flag to select image size on creation
- [x] console only run
