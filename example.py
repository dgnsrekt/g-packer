from g_packer.packer import PackageMaster, VersionOnePackageProcessor
from g_packer.manifest import ManifestMaker
from g_packer.manifest import FileManifest, MultipleFileManifest


def main():

    target_folder = "stuff"  # FOLDER TO PACK make sure folder or file exists.

    buffer_size = (1024 * 1024) * 2

    manifest = ManifestMaker.create(target_folder, buffer_size)  # createst a manifest object

    ManifestMaker.write(manifest, "manifest.ini", buffer_size)  # writes to a manifest.ini file

    PackageMaster.pack(manifest, buffer_size, VersionOnePackageProcessor, "package.dat")
    # ^--- reads then serializes each file in the manifest by BUFFER_SIZE chunks.
    # Uses the VersionOnePackageProcessor to read and serailize each file in the manifest
    # file by BUFFER_SIZE chunks then writes to the data to a package.dat file.
    # PackageProcessor takes care of compress -> metadata collection -> serialization -> writing package.dat
    # The packageProcessor can easily be upgraded to encrypt each chunk prior to compress/ serialization.

    PackageMaster.unpack("package.dat", "new_folder")
    # Takes care of unpacking a package.dat file and writes to the root new_folder directory.


if __name__ == "__main__":
    main()
