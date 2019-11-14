import zlib
from hashlib import sha256
from pathlib import Path

import bson

from .static import ALLOWED_CHUNK_SIZES
from .manifest import FileManifest  # used for typing


class BasePacker:
    version = None

    def hash():
        raise NotImplementedError

    #    def encrypt():
    #        raise NotImplementedError

    def compress():
        raise NotImplementedError

    def collect_metadata():
        raise NotImplementedError

    def serialize():
        raise NotImplementedError

    def write_package():
        raise NotImplementedError


class BaseUnPacker:
    version = None

    def parse_metadata():
        raise NotImplementedError

    def decompress():
        raise NotImplementedError

    # def decrypt():
    # raise NotImplementedError

    def hash():
        raise NotImplementedError

    def compare_hash():
        raise NotImplementedError

    def write():
        raise NotImplementedError


class VersionOnePackageProcessor(BasePacker, BaseUnPacker):
    """
    Version 1 Package Processor
    Extends from the Packer/Unpacker base classes and provides functions
    needed to encrypt, compress, serailize, deserialize pack and unpack
    multiple files into a single package.dat file.
    """

    version = 1

    def hash(file_chunk):
        """Returns the first/last bytes of the sha256 hash of the input chunk."""
        hash_algo = sha256()
        file_hash = hash_algo.update(file_chunk)
        file_hash = hash_algo.hexdigest()

        first_bytes = file_hash[:4]
        last_bytes = file_hash[-4:]

        return first_bytes + last_bytes

    def compress(file_chunk):
        """Returns the compressed version of a file chunk."""

        # save_bytes = len(file_chunk) - len(compressed_chunk)  # noqa
        # print("using compressed chunk")  # TODO: add else for logging.

        compressed_chunk = zlib.compress(file_chunk, level=9)
        if len(compressed_chunk) < len(file_chunk):
            return compressed_chunk, True
        else:
            return file_chunk, False

    def collect_metadata(file_name, chunk_hash, index, seek, compressed_flag):
        """Collects and returns metadata of the file."""
        meta_data = {
            "filename": file_name,
            "hash": chunk_hash,
            "index": index,
            "seek": seek,
            "compressed": compressed_flag,
            "version": VersionOnePackageProcessor.version,
        }
        # print(meta_data)
        return meta_data

    def serialize(data):
        """Returns a bson encoded version of the inputted data chunk."""
        return bson.encode(data)

    def write_package(serialized_data, destination):
        """Appends a serialized data chunk to the destination file."""
        with open(destination, mode="ab") as write_file:
            return write_file.write(serialized_data)

    #################### Unpacker Section ####################

    def parse_metadata(chunk):
        """Parses and returns a dictionary of metadata from a chunk."""
        meta_data = {
            "version": chunk["version"],
            "filename": chunk["filename"],
            "hash": chunk["hash"],
            "index": chunk["index"],  # TODO: used for logging/ progres bar/ or resume feature
            "seek": chunk["seek"],  # mayuse to resume
            "compressed": chunk["compressed"],
        }
        return meta_data

    def decompress(payload, compressed_flag):
        """Decompresses payload if the compressed_flag is True"""
        if compressed_flag:
            return zlib.decompress(payload)
        else:
            return payload

    def compare_hash(chunk_hash, other_hash):  # Comparehash
        """Returns true if the chunk_hash == the other_hash"""
        assert chunk_hash == other_hash  # TODO: Proper exception # should return, better naming

    def write(cleaned_data, filename, root_folder):

        folder = Path(root_folder)

        file_path = Path(f"{folder}{filename}")
        # TODO: Think about passing permissions as metadata

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)

        with open(file_path, mode="ab") as write_file:
            return write_file.write(cleaned_data)


class PackageMaster:
    versions = {1: VersionOnePackageProcessor}

    def split(data):
        """Splits the payload, version from the metadata."""
        payload = data.pop("payload")
        version = data.pop("version")
        return payload, data, version

    def get_package_processor(version):
        """Returns the proper processer based on the version arg."""
        processor = PackageMaster.versions.get(version, None)
        assert processor is not None  # TODO: Add proper error.
        return processor

    def unpack(target_package: str, destination_root_folder: str):
        """Processes and Unpacks a package.dat into the destination folder"""
        with open(target_package, mode="rb") as read_file:
            for deserialized_data in bson.decode_file_iter(read_file):

                payload, meta_data, version = PackageMaster.split(deserialized_data)

                processor = PackageMaster.get_package_processor(version)

                payload = processor.decompress(payload, meta_data["compressed"])

                chunk_hash = processor.hash(payload)

                processor.compare_hash(chunk_hash, meta_data["hash"])

                processor.write(payload, meta_data["filename"], destination_root_folder)
                print(".", end="", flush=True)

    def pack(
        manifest: FileManifest, chunk_buffer_size: int, processor: BasePacker, destination: str
    ):
        """Process and Packs all manifested files into a package.dat file."""

        assert issubclass(
            processor, BasePacker
        ), "This is not a Package Processor"  # TODO if , raise error
        assert chunk_buffer_size in ALLOWED_CHUNK_SIZES

        manifest.verify()

        seek = 0  # For recording the start location of each file.

        for current_file in manifest:

            chunks = current_file.chunk_len(chunk_buffer_size)

            file_name = str(current_file.path).split(f"{manifest.top_directory}")[-1]

            with open(current_file.path, "rb") as read_file:
                for index in range(chunks):
                    chunk = read_file.read(chunk_buffer_size)

                    chunk_hash = processor.hash(chunk)

                    chunk, compressed_flag = processor.compress(chunk)

                    data = processor.collect_metadata(
                        file_name, chunk_hash, index, seek, compressed_flag
                    )
                    data["payload"] = chunk

                    serialized_data = processor.serialize(data)

                    written_bytes = processor.write_package(serialized_data, destination)

                    seek += written_bytes
                    print(".", end="", flush=True)
