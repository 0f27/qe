def test_get_folder_size_sums_nested_files(qe_module, tmp_path):
    (tmp_path / "one.bin").write_bytes(b"123")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "two.bin").write_bytes(b"4567")

    assert qe_module.get_folder_size(str(tmp_path)) == 7


def test_get_fat_folders_returns_empty_without_folders(qe_module):
    assert qe_module.get_fat_folders(None) == []
    assert qe_module.get_fat_folders([]) == []


def test_get_fat_folders_skips_missing_paths(qe_module, tmp_path, capsys):
    missing = tmp_path / "missing"

    assert qe_module.get_fat_folders([str(missing)]) == []
    assert "Warning: Folder not found, skipping:" in capsys.readouterr().out


def test_get_fat_folders_skips_files(qe_module, tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a folder")

    assert qe_module.get_fat_folders([str(file_path)]) == []
    assert "Warning: Not a directory, skipping:" in capsys.readouterr().out


def test_get_fat_folders_mounts_folder_readonly_by_default(qe_module, tmp_path):
    folder = tmp_path / "shared"
    folder.mkdir()

    assert qe_module.get_fat_folders([str(folder)], start_index=5) == [
        "-drive",
        f"file=fat:ro:{folder},index=5,format=raw,media=disk,if=virtio",
    ]


def test_get_fat_folders_mounts_folder_readwrite(qe_module, tmp_path):
    folder = tmp_path / "shared"
    folder.mkdir()

    assert qe_module.get_fat_folders([f"{folder}:rw"], start_index=6) == [
        "-drive",
        f"file=fat:rw:{folder},index=6,format=raw,media=disk,if=virtio",
    ]


def test_get_fat_folders_uses_fat32_for_large_folder(qe_module, tmp_path, monkeypatch):
    folder = tmp_path / "large"
    folder.mkdir()
    monkeypatch.setattr(qe_module, "get_folder_size", lambda path: 401 * 1024 * 1024)

    assert qe_module.get_fat_folders([str(folder)], start_index=7) == [
        "-drive",
        f"file=fat:ro:{folder},fat-type=32,index=7,format=raw,media=disk,if=virtio",
    ]


def test_get_fat_folders_increments_indexes(qe_module, tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    assert qe_module.get_fat_folders([str(first), str(second)], start_index=8) == [
        "-drive",
        f"file=fat:ro:{first},index=8,format=raw,media=disk,if=virtio",
        "-drive",
        f"file=fat:ro:{second},index=9,format=raw,media=disk,if=virtio",
    ]
