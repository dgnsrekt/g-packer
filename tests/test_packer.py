import pytest
from pathlib import Path
from g_packer.packer import PackageMaster, VersionOnePackageProcessor
from g_packer.manifest import ManifestMaker, PackagePath
from g_packer.static import MEGABYTE

from .data_generator import FakeFileGenerator
from os import walk


def test_imports():
    pass


@pytest.fixture(scope="session")
def fake_test_dirs(tmpdir_factory):

    FILE_SIZE = 10  # HOW MANY MEGABYTES PER FAKE FILE

    pre_data_dir = Path(tmpdir_factory.mktemp("pre_data"))
    post_data_dir = Path(tmpdir_factory.mktemp("post_data"))
    pack_data_dir = tmpdir_factory.mktemp("package_data")

    package_dat = pack_data_dir.join("package.dat")
    package_dat = Path(package_dat)
    package_dat.touch()

    assert pre_data_dir.exists()
    assert post_data_dir.exists()

    fake_generator = FakeFileGenerator(pre_data_dir)
    fake_generator.generate_files(num_directories=2, num_files=2)
    fake_generator.generate_data(FILE_SIZE)

    return pre_data_dir, post_data_dir, fake_generator, package_dat


def test_pack_and_unpack(fake_test_dirs):
    pre_data_dir, post_data_dir, fake_generator, package_dat = fake_test_dirs

    buffer_size = 1 * MEGABYTE

    manifest = ManifestMaker.create(pre_data_dir, buffer_size)

    PackageMaster.pack(
        manifest, buffer_size, VersionOnePackageProcessor, str(package_dat)
    )

    assert package_dat.exists()

    PackageMaster.unpack(str(package_dat), str(post_data_dir))

    pre_files = []
    post_files = []

    for pre_dir_, sub_, files_ in walk(pre_data_dir):
        for f in files_:
            pre_files.append(f"{pre_dir_}/{f}")

    for post_dir_, sub_, files_ in walk(post_data_dir):
        for f in files_:
            post_files.append(f"{post_dir_}/{f}")

    pre_files = [PackagePath(f) for f in pre_files]
    post_files = [PackagePath(f) for f in post_files]

    for pre, post in zip(pre_files, post_files):
        assert pre.sha256sum() == post.sha256sum()
