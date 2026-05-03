import io
import json
import tarfile

import pytest


def test_set_defaults_creates_config_file(qe_module, tmp_path, monkeypatch):
    config_folder = tmp_path / "qe"
    monkeypatch.setattr(qe_module, "config_folder", str(config_folder))
    defaults = {"memory": "3G", "cpu_cores": "2", "image_size_to_create": "40G"}

    assert qe_module.set_defaults(defaults) == defaults
    assert json.loads((config_folder / "config.json").read_text()) == defaults


def test_set_defaults_reads_existing_config_file(qe_module, tmp_path, monkeypatch):
    config_folder = tmp_path / "qe"
    config_folder.mkdir()
    configured = {"memory": "8G", "cpu_cores": "4", "image_size_to_create": "100G"}
    (config_folder / "config.json").write_text(json.dumps(configured))
    monkeypatch.setattr(qe_module, "config_folder", str(config_folder))

    assert qe_module.set_defaults({"memory": "3G"}) == configured


def test_get_bios_and_acceleration_uses_existing_bios(qe_module, tmp_path, monkeypatch):
    bios = tmp_path / "OVMF.fd"
    bios.write_bytes(b"bios")
    families = {"linux": {"accel": ["-enable-kvm"], "bios_paths": [str(bios)]}}
    monkeypatch.setattr(qe_module, "os_family", "linux")

    assert qe_module.get_bios_and_acceleration(families) == (
        str(bios),
        ["-enable-kvm"],
    )


def test_get_bios_and_acceleration_downloads_missing_bios(
    qe_module, tmp_path, monkeypatch
):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b"downloaded bios"

    config_folder = tmp_path / "qe"
    config_folder.mkdir()
    families = {"linux": {"accel": ["-enable-kvm"], "bios_paths": []}}
    monkeypatch.setattr(qe_module, "config_folder", str(config_folder))
    monkeypatch.setattr(qe_module, "os_family", "linux")
    monkeypatch.setattr(qe_module.urllib.request, "urlopen", lambda url: Response())

    assert qe_module.get_bios_and_acceleration(families) == (
        str(config_folder / "OVMF.fd"),
        ["-enable-kvm"],
    )
    assert (config_folder / "OVMF.fd").read_bytes() == b"downloaded bios"


def test_get_bios_and_acceleration_rejects_unsupported_os(qe_module, monkeypatch):
    monkeypatch.setattr(qe_module, "os_family", "darwin")

    with pytest.raises(NotImplementedError):
        qe_module.get_bios_and_acceleration({"darwin": None})


def test_extract_ova_returns_extracted_vmdk(qe_module, tmp_path):
    ova_path = tmp_path / "appliance.ova"
    tar_info = tarfile.TarInfo("disk.vmdk")
    tar_data = b"vmdk contents"
    tar_info.size = len(tar_data)
    with tarfile.open(ova_path, "w") as archive:
        archive.addfile(tar_info, io.BytesIO(tar_data))

    extracted = qe_module.extract_ova(str(ova_path))

    assert extracted == str(tmp_path / "appliance.vmdk")
    assert (tmp_path / "appliance.vmdk").read_bytes() == tar_data
    assert not (tmp_path / "appliance").exists()


def test_extract_ova_raises_without_vmdk(qe_module, tmp_path):
    ova_path = tmp_path / "appliance.ova"
    tar_info = tarfile.TarInfo("readme.txt")
    tar_data = b"not a disk"
    tar_info.size = len(tar_data)
    with tarfile.open(ova_path, "w") as archive:
        archive.addfile(tar_info, io.BytesIO(tar_data))

    with pytest.raises(ValueError):
        qe_module.extract_ova(str(ova_path))

    assert not (tmp_path / "appliance").exists()
