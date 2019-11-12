from pathlib import Path

from g_packer.packer import PackageMaster, VersionOnePacker
from g_packer.manifest import FileManifest, ManifestMaker


def protoype_code():

    target_folder = "stuff/movie.mkv"
    # target_folder = "stuff"

    path = Path("package.dat")

    path.touch()
    path.unlink()

    buffer_size = (1024 * 1024) * 2

    manifest = ManifestMaker.create(target_folder, buffer_size)

    ManifestMaker.write(manifest, "manifest.ini", buffer_size)

    PackageMaster.pack(manifest, buffer_size, VersionOnePacker, "package.dat")

    PackageMaster.unpack("package.dat")


if __name__ == "__main__":
    protoype_code()
