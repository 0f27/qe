import pytest


def test_parse_usb_spec_accepts_vendor_product_pair(qe_module):
    assert (
        qe_module.parse_usb_spec("046D:C534")
        == "usb-host,vendorid=0x046d,productid=0xc534"
    )


def test_parse_usb_spec_accepts_bus_addr_pair(qe_module):
    assert qe_module.parse_usb_spec("bus=1,addr=4") == "usb-host,hostbus=1,hostaddr=4"


def test_parse_usb_spec_accepts_qemu_vendor_product_pair(qe_module):
    assert (
        qe_module.parse_usb_spec("vendorid=0x1050,productid=0x0407")
        == "usb-host,vendorid=0x1050,productid=0x0407"
    )


@pytest.mark.parametrize("spec", ["046d", "046d:c534:extra", "bus=one,addr=4"])
def test_parse_usb_spec_rejects_invalid_values(qe_module, spec):
    with pytest.raises(ValueError):
        qe_module.parse_usb_spec(spec)


def test_parse_lsusb_line(qe_module):
    assert qe_module.parse_lsusb_line(
        "Bus 001 Device 004: ID 046d:c534 Logitech, Inc. Unifying Receiver"
    ) == {
        "bus": "001",
        "device": "004",
        "vendor_id": "046d",
        "product_id": "c534",
        "description": "Logitech, Inc. Unifying Receiver",
    }


def test_get_usb_devices_adds_one_controller_for_multiple_devices(qe_module):
    assert qe_module.get_usb_devices(["046d:c534", "1050:0407"]) == [
        "-device",
        "qemu-xhci",
        "-device",
        "usb-host,vendorid=0x046d,productid=0xc534",
        "-device",
        "usb-host,vendorid=0x1050,productid=0x0407",
    ]


def test_select_usb_devices_accepts_comma_separated_indexes(qe_module, monkeypatch):
    devices = [
        {
            "bus": "001",
            "device": "004",
            "vendor_id": "046d",
            "product_id": "c534",
            "description": "Keyboard",
        },
        {
            "bus": "002",
            "device": "010",
            "vendor_id": "1050",
            "product_id": "0407",
            "description": "Security Key",
        },
    ]
    monkeypatch.setattr("builtins.input", lambda prompt: "2,1")

    assert qe_module.select_usb_devices(devices) == [
        "usb-host,hostbus=2,hostaddr=10",
        "usb-host,hostbus=1,hostaddr=4",
    ]
