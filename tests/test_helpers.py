import pytest


def test_is_image_detects_supported_images_and_devices(qe_module):
    assert qe_module.is_image("vm.iso")
    assert qe_module.is_image("vm.qcow2")
    assert qe_module.is_image("vm.vmdk")
    assert qe_module.is_image("vm.vhd.vtoy")
    assert qe_module.is_image("/dev/sda")


def test_is_image_rejects_non_image_arguments(qe_module):
    assert not qe_module.is_image("-m")
    assert not qe_module.is_image("2048")
    assert not qe_module.is_image("-net")
    assert not qe_module.is_image("notes.txt")


def test_parse_folder_arg_defaults_to_readonly(qe_module):
    assert qe_module.parse_folder_arg("./shared") == ("./shared", True)


def test_parse_folder_arg_accepts_rw_and_ro_suffixes(qe_module):
    assert qe_module.parse_folder_arg("./shared:rw") == ("./shared", False)
    assert qe_module.parse_folder_arg("./shared:ro") == ("./shared", True)


def test_parse_port_mapping_accepts_host_guest_pair(qe_module):
    assert qe_module.parse_port_mapping("8080:80") == (8080, 80)


@pytest.mark.parametrize("port", ["8080", "8080:80:extra", "host:guest"])
def test_parse_port_mapping_rejects_invalid_values(qe_module, port):
    with pytest.raises(ValueError):
        qe_module.parse_port_mapping(port)


def test_image_metadata_helpers(qe_module):
    assert qe_module.get_image_format("vm.qcow2") == "qcow2"
    assert qe_module.get_image_format("vm.vhd") == "vpc"
    assert qe_module.get_image_format("vm.vhd.vtoy") == "vpc"
    assert qe_module.get_image_format("vm.vdi.vtoy") == "vdi"
    assert qe_module.get_media_type("installer.iso") == "cdrom"
    assert qe_module.get_media_type("vm.qcow2") == "disk"


def test_get_image_format_rejects_unknown_extension(qe_module):
    with pytest.raises(ValueError):
        qe_module.get_image_format("vm.unknown")


def test_build_drive_args(qe_module):
    assert qe_module.build_drive_args("vm.qcow2", 3) == [
        "-drive",
        "file=vm.qcow2,format=qcow2,index=3,media=disk",
    ]


def test_windows_and_sudo_detection(qe_module):
    assert qe_module.is_windows_image("w11.qcow2")
    assert qe_module.is_windows_image("WindowsServer.vhd")
    assert not qe_module.is_windows_image("ubuntu.qcow2")
    assert qe_module.needs_sudo("/dev/nvme0n1")
    assert not qe_module.needs_sudo("vm.raw")
