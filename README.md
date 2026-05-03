# QE - powerful and easy to use command line virtual machine launcher based on Qemu

> I use it myself, so expect minor bugs and hidden features.
> If you find something, feel free to open issue or create pull request.

## Usage Examples

Run `qe --help` for full usage information.

```bash
qe [images] [options] [qemu-system-* options]
```

Run an existing VM image or live ISO:

```bash
qe w11.vmdk
qe Fedora-KDE-Live-x86_64-40-1.14.iso
```

Create a new image if it does not exist and start installation from ISO:

```bash
qe ubuntu.qcow2 ~/Downloads/ubuntu-24.04-desktop-amd64.iso
qe new.qcow2 --size 20G
```

Run without saving disk changes, or without GUI:

```bash
qe arch.qcow2 -s
qe Fedora-Live.iso -c
```

Use UEFI by default, or boot in legacy BIOS mode:

```bash
qe MX.qcow2 --no-efi
```

Pass QEMU arguments through QE:

```bash
qe kali.qcow2 -s -net none
```

Generate a QEMU command without running it:

```bash
qe windows-server-2022.vhd -n
# qemu-system-x86_64 -enable-kvm -smp 2 -m 4G -bios /usr/share/ovmf/x64/OVMF.fd -drive file=windows-server-2022.vhd,format=vpc,index=0,media=disk -display sdl
```

Mount files and folders:

```bash
# Create ./drivers.iso from a folder or file and mount it
qe vm.qcow2 -i ./drivers

# Mount host folders as FAT drives
qe vm.qcow2 -f ./shared
qe vm.qcow2 -f ./shared:rw
qe vm.qcow2 -f ./drivers -f ./shared:rw
```

Forward ports from host to guest:

```bash
qe vm.qcow2 --port 8080:80
qe vm.qcow2 -p --port 3306:3306
```

Run a physical HDD, SSD, or NVMe device as a VM:

```bash
qe /dev/sda --snapshot
```

Create and run [Ventoy](https://ventoy.net/en/index.html) [vtoyboot](https://ventoy.net/en/plugin_vtoyboot.html) and [vhdboot](https://ventoy.net/en/plugin_vhdboot.html) images to launch from USB:

```bash
qe w11.vhd.vtoy Win11_23H2_English_x64v2.iso -i ./drivers_and_software
mv w11.vhd.vtoy w11.vhd
```

Pass host USB devices directly into the guest with `-u` / `--usb`:

```bash
# Select interactively from lsusb output
qe vm.qcow2 -u

# Pass by vendor/product ID, host bus/address, or QEMU-style IDs
qe vm.qcow2 --usb 046d:c534
qe vm.qcow2 --usb bus=1,addr=4
qe vm.qcow2 --usb vendorid=0x046d,productid=0xc534

# Pass through several USB devices
qe vm.qcow2 --usb 046d:c534 --usb 1050:0407
```

Use `lsusb` to find vendor/product IDs and bus/device numbers:

```bash
lsusb
# Bus 001 Device 004: ID 046d:c534 Logitech, Inc. Unifying Receiver
```

USB passthrough may require access to `/dev/bus/usb/...`. If QEMU cannot open the device, run QE with suitable permissions or configure udev rules for your user.

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

## Tests

Run the automatic tests with:

```bash
pytest
```

## TODO

- [x] image creation if not exists
- [x] config in json
- [x] -display sdl if windows image
- [x] fat folders
- [x] usb device selection and passthrough
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
- [x] tests!
- [ ] add network setup to connect several VM instances
- [x] beautify --help
- [x] add flag for fixed size images
- [x] add flag to select image size on creation
- [x] console only run
