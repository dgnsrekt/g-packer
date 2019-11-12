from pathlib import Path

from g_packer.packer import PackageMaster, V1_Packer
from g_packer.manifest import FileManifest, Manifest


def protoype_code():

    multi_target = "stuff"
    from time import sleep

    p = Path("package.dat")

    p.touch()
    p.unlink()

    process = V1_Packer
    chunk_buffer_size = (1024 * 1024) * 2
    current = Manifest.make(multi_target)
    PackageMaster.pack(current, chunk_buffer_size, process, "package.dat")
    sleep(5)
    PackageMaster.unpack("package.dat")


if __name__ == "__main__":
    protoype_code()
