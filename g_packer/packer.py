import zlib
from hashlib import sha256

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

    def parse_metadata(chunk):
        raise NotImplementedError

    def decompress():
        raise NotImplementedError

    # def decrypt():
    # raise NotImplementedError

    def hash():
        raise NotImplementedError

    def check_hash():
        raise NotImplementedError

    def write():
        raise NotImplementedError


class VersionOnePackageProcessor(BasePacker, BaseUnPacker):
    version = 1

    def hash(file_chunk):
        hash_algo = sha256()
        file_hash = hash_algo.update(file_chunk)
        file_hash = hash_algo.hexdigest()

        first_bytes = file_hash[:4]
        last_bytes = file_hash[-4:]

        return first_bytes + last_bytes

    def compress(file_chunk):

        # save_bytes = len(file_chunk) - len(compressed_chunk)  # noqa
        # print("using compressed chunk")  # TODO: add else for logging.

        compressed_chunk = zlib.compress(file_chunk, level=9)
        if len(compressed_chunk) < len(file_chunk):
            return compressed_chunk, True
        else:
            return file_chunk, False

    def collect_metadata(file_name, chunk_hash, index, seek, compressed_flag):
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
        return bson.encode(data)

    def write_package(serialized_data, destination):
        # print("writing bytes to file")
        with open(destination, mode="ab") as write_file:
            return write_file.write(serialized_data)

    ################### Unpacker Section
    def parse_metadata(chunk):
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
        if compressed_flag:
            return zlib.decompress(payload)
        else:
            return payload

    def check_hash(first_hash, second_hash):  # Comparehash
        assert first_hash == second_hash  # TODO: Proper exception # should return, better naming

    def write(deserialized_data, destination):
        # print("writing bytes to file")
        destination += "new"
        with open(destination, mode="ab") as write_file:
            return write_file.write(deserialized_data)


class PackageMaster:
    versions = {1: VersionOnePackageProcessor}

    def split(data):
        payload = data.pop("payload")
        version = data.pop("version")
        return payload, data, version

    def get_package_processor(version):
        processor = PackageMaster.versions.get(version, None)
        assert processor is not None  # TODO: Add proper error.
        return processor

    def unpack(target_package: str):  # TODO: ADD root_destination
        with open(target_package, mode="rb") as read_file:
            for deserialized_data in bson.decode_file_iter(read_file):

                payload, meta_data, version = PackageMaster.split(deserialized_data)

                processor = PackageMaster.get_package_processor(version)

                payload = processor.decompress(payload, meta_data["compressed"])

                chunk_hash = processor.hash(payload)

                processor.check_hash(chunk_hash, meta_data["hash"])

                processor.write(
                    payload, meta_data["filename"]
                )  # TODO: need to add file destination
                print(".", end="", flush=True)

    def pack(
        manifest: FileManifest, chunk_buffer_size: int, processor: BasePacker, destination: str
    ):

        assert issubclass(
            processor, BasePacker
        ), "This is not a Package Processor"  # TODO if , raise error
        assert chunk_buffer_size in ALLOWED_CHUNK_SIZES

        manifest.verify()

        seek = 0  # Shows the starting location to start read the file from the package.dat.

        for current_file in manifest:
            if current_file.is_dir():

                print(current_file)
                print(current_file.name)
                print(current_file.is_dir())
                exit()

            file_name = str(current_file.path)
            chunks = current_file.chunk_len(chunk_buffer_size)

            # print("chunks:", chunks)

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

                    # break  # TODO: DONT FORGET TO REMOVE
