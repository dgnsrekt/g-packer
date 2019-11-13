from pathlib import Path

from g_packer.packer import PackageMaster, VersionOnePackageProcessor
from g_packer.manifest import ManifestMaker
from g_packer.manifest import FileManifest, MultipleFileManifest


def protoype_code():

    # target_folder = "stuff/movie.mkv"
    target_folder = "stuff"

    path = Path("package.dat")

    path.touch()
    path.unlink()

    buffer_size = (1024 * 1024) * 2

    manifest = ManifestMaker.create(target_folder, buffer_size)

    ManifestMaker.write(manifest, "manifest.ini", buffer_size)

    PackageMaster.pack(manifest, buffer_size, VersionOnePackageProcessor, "package.dat")

    PackageMaster.unpack("package.dat")


if __name__ == "__main__":
    protoype_code()
