from g_packer.packer import PackageMaster, VersionOnePackageProcessor
from g_packer.manifest import ManifestMaker
from g_packer.manifest import FileManifest, MultipleFileManifest
from g_packer.static import MEGABYTE


def main():

    target_pack_folder = "stuff"  # FOLDER TO PACK make sure folder or file exists.
    target_unpack_folder = "new_folder"

    target_manifest_location = "manifest.ini"
    target_package_dat_location = "package.dat"

    buffer_size = MEGABYTE * 2

    manifest = ManifestMaker.create(target_pack_folder, buffer_size)  # createst a manifest object

    ManifestMaker.write(
        manifest, target_manifest_location, buffer_size
    )  # writes to a manifest.ini file

    PackageMaster.pack(
        manifest, buffer_size, VersionOnePackageProcessor, target_package_dat_location
    )
    # ^--- reads then serializes each file in the manifest by BUFFER_SIZE chunks.
    # Uses the VersionOnePackageProcessor to read and serailize each file in the manifest
    # file by BUFFER_SIZE chunks then writes to the data to a package.dat file.
    # PackageProcessor takes care of compress -> metadata collection -> serialization -> writing package.dat
    # The packageProcessor can easily be upgraded to encrypt each chunk prior to compress/ serialization.

    PackageMaster.unpack("package.dat", target_unpack_folder)
    # Takes care of unpacking a package.dat file and writes to the root new_folder directory.


if __name__ == "__main__":
    main()
