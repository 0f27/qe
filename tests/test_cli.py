import sys


def run_main(qe_module, monkeypatch, tmp_path, argv):
    calls = []
    config_folder = tmp_path / "config"
    monkeypatch.setattr(qe_module, "config_folder", str(config_folder))
    monkeypatch.setattr(qe_module, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        qe_module,
        "get_bios_and_acceleration",
        lambda families: ("OVMF.fd", ["-enable-kvm"]),
    )
    monkeypatch.setattr(qe_module, "run", lambda args: calls.append(args))
    monkeypatch.setattr(sys, "argv", ["qe"] + argv)

    qe_module.main()

    return calls


def printed_command(capsys):
    return capsys.readouterr().out.strip().split()


def test_main_dry_run_prints_qemu_command_without_running(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")

    calls = run_main(qe_module, monkeypatch, tmp_path, [str(image), "-n"])

    assert calls == []
    assert printed_command(capsys) == [
        "qemu-system-x86_64",
        "-enable-kvm",
        "-smp",
        "2",
        "-m",
        "3G",
        "-bios",
        "OVMF.fd",
        "-drive",
        f"file={image},format=qcow2,index=0,media=disk",
    ]


def test_main_no_efi_excludes_bios_from_command(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")

    run_main(qe_module, monkeypatch, tmp_path, [str(image), "--no-efi", "-n"])

    command = printed_command(capsys)
    assert "-bios" not in command
    assert "OVMF.fd" not in command


def test_main_snapshot_adds_snapshot_flag(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")

    run_main(qe_module, monkeypatch, tmp_path, [str(image), "--snapshot", "-n"])

    assert printed_command(capsys)[-1] == "-snapshot"


def test_main_console_adds_nographic_and_removes_windows_display(
    qe_module, tmp_path, monkeypatch, capsys
):
    image = tmp_path / "w11.qcow2"
    image.write_bytes(b"image")

    run_main(qe_module, monkeypatch, tmp_path, [str(image), "--console", "-n"])

    command = printed_command(capsys)
    assert "-nographic" in command
    assert "-display" not in command
    assert "sdl" not in command


def test_main_preserves_qemu_args_and_avoids_default_mem_cpu(
    qe_module, tmp_path, monkeypatch, capsys
):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")

    run_main(
        qe_module,
        monkeypatch,
        tmp_path,
        [str(image), "-m", "8G", "-smp", "4", "-net", "none", "-n"],
    )

    command = printed_command(capsys)
    assert command.count("-m") == 1
    assert command.count("-smp") == 1
    assert command[command.index("-m") + 1] == "8G"
    assert command[command.index("-smp") + 1] == "4"
    assert command[command.index("-net") + 1] == "none"


def test_main_ports_and_fat_folder_are_included(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")
    folder = tmp_path / "shared"
    folder.mkdir()

    run_main(
        qe_module,
        monkeypatch,
        tmp_path,
        [str(image), "-p", "--port", "8080:80", "-f", f"{folder}:rw", "-n"],
    )

    command = printed_command(capsys)
    assert "-nic" in command
    nic = command[command.index("-nic") + 1]
    assert "hostfwd=tcp:127.0.0.1:9922-0.0.0.0:22" in nic
    assert "hostfwd=tcp:127.0.0.1:8080-0.0.0.0:80" in nic
    assert "-drive" in command
    assert (
        f"file=fat:rw:{folder},index=10,format=raw,media=disk,if=virtio"
        in command
    )


def test_main_usb_passthrough_is_included(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "vm.qcow2"
    image.write_bytes(b"image")

    run_main(qe_module, monkeypatch, tmp_path, [str(image), "--usb", "046d:c534", "-n"])

    command = printed_command(capsys)
    assert "-device" in command
    assert "qemu-xhci" in command
    assert "usb-host,vendorid=0x046d,productid=0xc534" in command


def test_main_size_overrides_created_image_size(qe_module, tmp_path, monkeypatch, capsys):
    image = tmp_path / "new.qcow2"

    calls = run_main(qe_module, monkeypatch, tmp_path, [str(image), "--size", "20G", "-n"])

    assert calls == [["qemu-img", "create", "-f", "qcow2", str(image), "20G"]]
    assert f"file={image},format=qcow2,index=0,media=disk" in printed_command(capsys)
