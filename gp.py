# flake8: noqa

import bson
import logme
from decouple import config
from environment import PACKAGE_DAT_PATH, MANIFEST_PATH
import math
import toml
import zlib
import hashlib


from pathlib import Path
from os import walk

MB = 1024 * 1024
MAX_BUFFER_SIZE = config("MAX_BUFFER_SIZE", cast=int) * MB

from data_gen import FakeFileGenerator  # remove this when done.
from environment import PRE_PROCESS_DATA, POST_PROCESS_DATA

from util import timeit

# gp should be an independent function that takes a folder as input.
logger = logme.log(scope="module", name="packer")


@timeit
def pack(directory_path: Path):
    buffer_position = 0
    file_position = 0

    for index, (directory, _, files) in enumerate(walk(directory_path)):
        for filename in files:

            payload = {}

            payload["directory"] = str(directory_path.name)

            filepath = Path(directory) / filename

            assert filepath.exists(), "File doesn't exists."
            filesize = filepath.stat().st_size

            total_chunks = math.ceil(
                filesize / MAX_BUFFER_SIZE  # TODO: CHECK WHeN FILE IS < BUFFER_SIZE
            )  # will take buffer as an input wont be constant

            # can reduce this to payload["n", "s", "b", "c"] to conserve space if needed
            payload["filename"] = str(filepath.relative_to(directory_path))
            payload["filesize"] = filesize
            payload["buffer_size"] = MAX_BUFFER_SIZE

            with open(filepath, mode="rb") as read_file:
                file_position += read_file.tell()
                payload["start_file"] = file_position

                while True:
                    hash = hashlib.sha256()
                    payload["chunks_left"] = total_chunks - 1

                    payload["start_chunk"] = read_file.tell()

                    chunk = read_file.read(MAX_BUFFER_SIZE)
                    # payload["hash_crc32"] = zlib.crc32(chunk)
                    hash.update(chunk)
                    payload["hash"] = hash.hexdigest()
                    compressed_chunk = zlib.compress(chunk, level=9)  # ADDED COMPRESSION HERE

                    payload["end_chunk"] = read_file.tell()

                    if not chunk:
                        logger.info(f"complete {filename}")
                        file_position += read_file.tell()
                        payload["end_file"] = file_position
                        break

                    payload["data"] = compressed_chunk
                    serialized_chunk = bson.encode(payload)

                    with open(PACKAGE_DAT_PATH, mode="ab") as write_file:
                        write_file.write(serialized_chunk)
                        total_chunks -= 1
                        print(".", end="", flush=True)

            payload.pop("data")
            payload.pop("start_chunk")
            payload.pop("end_chunk")
            payload.pop("chunks_left")

            manifest = payload.copy()

            with open(MANIFEST_PATH, mode="a") as write_manifest:
                if index == 1:
                    manifest_header = dict()
                    manifest_header["root_directory"] = manifest.get("directory")
                    manifest_header["buffer_size"] = manifest.get("buffer_size")
                    manifest_header_entry = toml.dumps(manifest_header)

                    write_manifest.write(manifest_header_entry)
                    write_manifest.write("\n")

                # manifest header
                manifest.pop("directory")
                manifest.pop("buffer_size")

                manifest["total_chunks"] = total_chunks

                _name = manifest.pop("filename")

                manifest_entry = toml.dumps({_name: manifest})
                write_manifest.write(manifest_entry)
                write_manifest.write("\n")


@timeit
def unpack(directory_path: Path):
    with open(directory_path, mode="rb") as read_file:
        for deserialized_chunk in bson.decode_file_iter(read_file):

            directory = deserialized_chunk["directory"]
            filename = deserialized_chunk["filename"]
            filesize = deserialized_chunk["filesize"]
            buffer_size = deserialized_chunk["buffer_size"]
            chunks = deserialized_chunk["chunks_left"]
            compressed_data = deserialized_chunk["data"]
            hash = deserialized_chunk["hash"]

            start = deserialized_chunk["start_chunk"]
            end = deserialized_chunk["end_chunk"]

            directory = POST_PROCESS_DATA / directory
            directory.mkdir(exist_ok=True)  # this has to go

            filename = directory / filename
            filename.parent.mkdir(exist_ok=True)
            filename.touch()

            read_hash = hashlib.sha256()

            with open(filename, mode="ab") as write_file:

                data = zlib.decompress(compressed_data)
                print("data_len", len(data))

                read_hash.update(data)
                hash_new = read_hash.hexdigest()

                print(directory)
                print("*" * 20)
                print("filesize", filesize)
                print(chunks)
                print(filename)
                print(hash)
                print(hash_new)
                print("start:", start)
                print("end:", end)
                assert hash == hash_new
                print()

                write_file.write(data)


def main():
    try:
        PACKAGE_DAT_PATH.unlink()
        MANIFEST_PATH.unlink()
    except:
        pass

    from time import sleep

    FILE_SIZE = 1024
    fake_maker = FakeFileGenerator(PRE_PROCESS_DATA, FILE_SIZE)

    with fake_maker.manager() as FFG:

        WORKING_DIRECTORY = list(PRE_PROCESS_DATA.glob("*"))[0]

        logger.info(f"WORKING DIRECTORY:\n{WORKING_DIRECTORY}")
        logger.info(f"BUFFER SIZE:{MAX_BUFFER_SIZE}\n")

        pack(WORKING_DIRECTORY)
        unpack(PACKAGE_DAT_PATH)
