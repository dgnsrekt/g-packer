from g_packer.manifest import PackagePath, FileManifest, MultipleFileManifest, SingleFileManifest
from os import getrandom
from pathlib import Path
from faker import Faker
from datetime import datetime

import pytest


def test_imports():
    pass


@pytest.fixture()
def raw_test_data():
    data = b"HELLO" * 1024
    expected_hash = "aa91b03be20d6e88664b2ae7cd56a699910dd75a8fb2ba053868f09c640454cf"
    return data, expected_hash


@pytest.fixture(scope="session")
def fake_test_file(tmp_path_factory):
    fake = Faker()
    file_name = fake.file_name()
    test_file = tmp_path_factory.mktemp("test") / file_name
    test_file.touch()

    return test_file


@pytest.fixture
def mock_package_path(monkeypatch, fake_test_file, raw_test_data):
    data, expected_hash = raw_test_data

    fake_test_file.write_bytes(data)

    package = PackagePath(fake_test_file.name)

    monkeypatch.setattr(package, "path", fake_test_file)

    return package, data, expected_hash


def test_package_path_sha256sum(mock_package_path):
    package, _, expected_hash = mock_package_path
    assert expected_hash == package.sha256sum()


def test_package_path_exists(mock_package_path):
    package, _, _ = mock_package_path
    assert package.path.exists() == True


def test_package_path_chunk_len(mock_package_path):
    package, _, _ = mock_package_path
    chunk_size = 1024
    assert package.chunk_len(chunk_size) == 5


def test_file_manifest_init_with_bad_buffersize_raises_error():
    with pytest.raises(ValueError) as verror:
        file_manfiest = FileManifest("test", 1000)


@pytest.fixture
def file_manifest_no_extras(fake_test_file, raw_test_data):
    data, expected_hash = raw_test_data

    buffer_size = 1024 * 1024

    fake_test_file.write_bytes(data)

    manifest = FileManifest(fake_test_file.name, buffer_size)

    return manifest, data, expected_hash


def test_file_manifest_top_directory_none(file_manifest_no_extras):
    manifest, data, expected_hash = file_manifest_no_extras

    assert manifest.top_directory is None


def test_file_manifesf_with_no_extras_creation_date(file_manifest_no_extras):
    manifest, data, expected_hash = file_manifest_no_extras
    date = manifest.extras["creation_date"]
    date = datetime.fromisoformat(date)
    assert type(date) == datetime

    assert len(manifest.extras.keys()) == 1


def test_file_manifest_with_no_extras_creation_date(file_manifest_no_extras):
    manifest, data, expected_hash = file_manifest_no_extras
    with pytest.raises(TypeError) as verror:
        manifest.verify()


@pytest.fixture
def file_manifest_with_extras(fake_test_file, raw_test_data):
    data, expected_hash = raw_test_data
    comment = "test_comment"
    created_by = "pytest"

    buffer_size = 1024 * 1024

    fake_test_file.write_bytes(data)

    manifest = FileManifest(
        fake_test_file.name, buffer_size, comment=comment, created_by=created_by
    )

    return manifest, data, expected_hash


def test_file_manifesf_with_extras(file_manifest_with_extras):
    manifest, data, expected_hash = file_manifest_with_extras
    date = manifest.extras["creation_date"]
    date = datetime.fromisoformat(date)

    assert type(date) == datetime

    assert len(manifest.extras.keys()) == 3

    assert set(manifest.extras.keys()) == set(["creation_date", "comment", "created_by"])
