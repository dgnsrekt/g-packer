from hashlib import sha256
from pathlib import Path
import zlib

from manifest import Manifest, FileManifest
from static import ALLOWED_CHUNK_SIZES

import bson


class Packer:
    version = None

    def hash():
        raise NotImplementedError

    #    def encrypt():
    #        raise NotImplementedError

    def compress():
        raise NotImplementedError

    def collect_metadata():
        raise NotImplementedError

    def serialize(data):
        raise NotImplementedError

    def write():
        raise NotImplementedError


class UnPacker:
    version = None

    def read_metadata(deserialized_chunk):
        meta_data = {}
        meta_data["version"] = deserialized_chunk.get("version")
        meta_data["filename"] = deserialized_chunk.get("filename")
        meta_data["hash"] = deserialized_chunk.get("hash")
        meta_data["index"] = deserialized_chunk.get("index")
        meta_data["seek"] = deserialized_chunk.get("seek")
        meta_data["compression"] = deserialized_chunk.get("compression")
        return meta_data

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


class V1_Packer(Packer):
    version = 1

    def hash(file_chunk):
        hash_ = sha256()
        hash_.update(file_chunk)
        hex_ = hash_.hexdigest()

        first_hash = hex_[:4]
        last_hash = hex_[-4:]

        return first_hash + last_hash

    def compress(file_chunk):
        return zlib.compress(file_chunk, level=9)

    def collect_metadata(file_name, chunk_hash, chunk_index, seek, compression_flag):
        meta_data = dict()
        meta_data["filename"] = file_name
        meta_data["hash"] = chunk_hash
        meta_data["index"] = chunk_index
        meta_data["seek"] = seek
        meta_data["compression"] = compression_flag
        meta_data["version"] = V1_Packer.version
        # print(meta_data)
        return meta_data

    def serialize(data):
        return bson.encode(data)

    def write(serialized_data, destination):
        # print("writing bytes to file")
        with open(destination, mode="ab") as write_file:
            return write_file.write(serialized_data)


class V1_UnPacker(UnPacker):
    version = 1

    def decompress(payload):
        return zlib.decompress(payload)

    def hash(file_chunk):
        hash_ = sha256()
        hash_.update(file_chunk)
        hex_ = hash_.hexdigest()

        first_hash = hex_[:4]
        last_hash = hex_[-4:]

        return first_hash + last_hash

    def check_hash(first_hash, second_hash):
        assert first_hash == second_hash  # TODO: Proper exception

    def write(deserialized_data, destination):
        # print("writing bytes to file")
        destination += "new"
        with open(destination, mode="ab") as write_file:
            return write_file.write(deserialized_data)


class PackageMaster:
    versions = {1: V1_UnPacker}

    def get_unpacker(version):
        processor = PackageMaster.versions.get(version, None)
        assert processor is not None  # TODO: Add proper error.
        return processor

    def unpack(target_package: str):
        with open(target_package, mode="rb") as read_file:
            for deserialized_data in bson.decode_file_iter(read_file):
                meta_data = UnPacker.read_metadata(deserialized_data)
                payload = deserialized_data.pop("payload")
                version = meta_data["version"]
                processor = PackageMaster.get_unpacker(version)

                # print(meta_data)
                # print(version)
                if meta_data["compression"]:  # TODO: Compare compression logic
                    payload = processor.decompress(payload)

                chunk_hash = processor.hash(payload)
                #  print(chunk_hash)
                processor.check_hash(chunk_hash, meta_data["hash"])

                file_name = meta_data.get("filename")
                processor.write(payload, file_name)  # TODO: need to add file destination
                print(".", end="", flush=True)

    def pack(manifest: FileManifest, chunk_len: int, processor: Packer, destination: str):

        assert chunk_len in ALLOWED_CHUNK_SIZES

        manifest.verify()
        seek = 0  # Shows the beginning position to read the file from.

        for file_ in manifest:
            filename = str(file_.path)
            chunks = file_.chunk_len(chunk_len)

            # print("chunks:", chunks)

            with open(file_.path, "rb") as read_file:
                for chunk_index in range(chunks):
                    compressed_flag = False

                    chunk = read_file.read(chunk_len)

                    chunk_hash = processor.hash(chunk)

                    compressed_chunk = processor.compress(chunk)

                    # compressed chunks < 90 bytes is useless.
                    if len(compressed_chunk) < len(chunk):
                        save_bytes = len(chunk) - len(compressed_chunk)

                        # print("saved_bytes:", save_bytes)
                        # print("using compressed chunk")  # TODO: add else for logging.

                        chunk = compressed_chunk
                        compressed_flag = True

                    data = processor.collect_metadata(
                        filename, chunk_hash, chunk_index, seek, compressed_flag
                    )
                    data["payload"] = chunk

                    serialized_data = processor.serialize(data)
                    written_bytes = processor.write(serialized_data, destination)

                    seek += written_bytes
                    print(".", end="", flush=True)

                    # break  # TODO: DONT FORGET TO REMOVE


def protoype_code():
    multi_target = "stuff"
    from time import sleep

    p = Path("package.dat")
    p.unlink()

    process = V1_Packer
    chunk_size = 1024 * 1024
    current = Manifest.make(multi_target)
    PackageMaster.pack(current, chunk_size, process, "package.dat")
    sleep(5)
    PackageMaster.unpack("package.dat")
