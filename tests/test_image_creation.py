import pytest


def test_create_isos_if_needed_returns_empty_without_sources(qe_module):
    assert qe_module.create_isos_if_needed(None) == []
    assert qe_module.create_isos_if_needed([]) == []


def test_create_isos_if_needed_skips_existing_iso(qe_module, tmp_path, monkeypatch):
    source = tmp_path / "drivers"
    source.mkdir()
    (tmp_path / "drivers.iso").write_bytes(b"iso")
    calls = []
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))

    assert qe_module.create_isos_if_needed([str(source)]) == [str(source) + ".iso"]
    assert calls == []


def test_create_isos_if_needed_invokes_mkisofs_for_missing_iso(qe_module, tmp_path, monkeypatch):
    source = tmp_path / "drivers"
    source.mkdir()
    calls = []
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))

    assert qe_module.create_isos_if_needed([str(source)]) == [str(source) + ".iso"]
    assert calls == [
        [
            "mkisofs",
            "-r",
            "-jcharset",
            "utf8",
            "-o",
            str(source) + ".iso",
            str(source),
        ]
    ]


def test_create_image_if_missing_skips_existing_image(qe_module, tmp_path, monkeypatch):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")
    calls = []
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))

    qe_module.create_image_if_missing(str(image), {"image_size_to_create": "40G"})

    assert calls == []


def test_create_image_if_missing_creates_dynamic_image(qe_module, tmp_path, monkeypatch):
    image = tmp_path / "vm.qcow2"
    calls = []
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))

    qe_module.create_image_if_missing(str(image), {"image_size_to_create": "20G"})

    assert calls == [["qemu-img", "create", "-f", "qcow2", str(image), "20G"]]


@pytest.mark.parametrize(
    ("image_name", "expected_options"),
    [
        ("vm.vhd", ["-o", "subformat=fixed"]),
        ("vm.vhd.vtoy", ["-o", "subformat=fixed"]),
        ("vm.vdi", ["-o", "static=on"]),
        ("vm.vdi.vtoy", ["-o", "static=on"]),
        ("vm.qcow2", ["-o", "preallocation=metadata"]),
    ],
)
def test_create_image_if_missing_uses_fixed_size_options(
    qe_module, tmp_path, monkeypatch, image_name, expected_options
):
    image = tmp_path / image_name
    calls = []
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))

    qe_module.create_image_if_missing(
        str(image),
        {"image_size_to_create": "30G"},
        fixed_size=True,
    )

    assert calls == [
        ["qemu-img", "create", "-f", qe_module.get_image_format(str(image))]
        + expected_options
        + [str(image), "30G"]
    ]


def test_identify_image_types_builds_drive_display_and_sudo(qe_module, monkeypatch):
    calls = []
    monkeypatch.setattr(
        qe_module,
        "create_image_if_missing",
        lambda image, defaults, fixed_size=False: calls.append((image, fixed_size)),
    )

    sudo, drive, display = qe_module.identify_image_types(
        ["/dev/sda", "w11.qcow2", "installer.iso"],
        {"image_size_to_create": "40G"},
        fixed_size=True,
    )

    assert sudo == ["sudo"]
    assert display == ["-display", "sdl"]
    assert drive == [
        "-drive",
        "file=/dev/sda,format=raw,index=0,media=disk",
        "-drive",
        "file=w11.qcow2,format=qcow2,index=1,media=disk",
        "-drive",
        "file=installer.iso,format=raw,index=2,media=cdrom",
    ]
    assert calls == [
        ("/dev/sda", True),
        ("w11.qcow2", True),
        ("installer.iso", True),
    ]
