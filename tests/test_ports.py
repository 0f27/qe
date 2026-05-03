import pytest


def test_add_ports_returns_empty_when_disabled(qe_module):
    defaults = {"ports_passthrough": {22: 9922}}

    assert qe_module.add_ports(False, None, defaults) == []
    assert qe_module.add_ports(False, [], defaults) == []


def test_add_ports_uses_default_mappings(qe_module):
    defaults = {"ports_passthrough": {22: 9922, 80: 9980}}

    assert qe_module.add_ports(True, None, defaults) == [
        "-nic",
        "user,hostfwd=tcp:127.0.0.1:9922-0.0.0.0:22,"
        "hostfwd=tcp:127.0.0.1:9980-0.0.0.0:80",
    ]


def test_add_ports_uses_custom_mappings(qe_module):
    defaults = {"ports_passthrough": {}}

    assert qe_module.add_ports(False, ["8080:80", "2222:22"], defaults) == [
        "-nic",
        "user,hostfwd=tcp:127.0.0.1:8080-0.0.0.0:80,"
        "hostfwd=tcp:127.0.0.1:2222-0.0.0.0:22",
    ]


def test_add_ports_custom_mapping_overrides_same_guest_default(qe_module):
    defaults = {"ports_passthrough": {22: 9922, 80: 9980}}

    assert qe_module.add_ports(True, ["2222:22"], defaults) == [
        "-nic",
        "user,hostfwd=tcp:127.0.0.1:2222-0.0.0.0:22,"
        "hostfwd=tcp:127.0.0.1:9980-0.0.0.0:80",
    ]


def test_add_ports_propagates_invalid_custom_port_error(qe_module):
    defaults = {"ports_passthrough": {}}

    with pytest.raises(ValueError):
        qe_module.add_ports(False, ["invalid"], defaults)
