from g_packer.manifest import PackagePath
from os import getrandom
from pathlib import Path
from faker import Faker

import pytest


def test_imports():
    pass


@pytest.fixture(scope="session")
def test_file(tmp_path_factory):
    FAKE = Faker()
    file_name = FAKE.file_name()
    test_file = tmp_path_factory.mktemp("test") / file_name
    test_file.touch()

    return test_file


@pytest.fixture
def mock_package_path(monkeypatch, test_file):
    data = b"HELLO" * 1024
    expected_hash = "aa91b03be20d6e88664b2ae7cd56a699910dd75a8fb2ba053868f09c640454cf"

    test_file.write_bytes(data)

    package = PackagePath(test_file.name)

    monkeypatch.setattr(package, "path", test_file)

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
