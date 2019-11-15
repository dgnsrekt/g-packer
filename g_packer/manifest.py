from abc import ABCMeta
from datetime import datetime
from hashlib import sha256
from math import ceil
from os import walk
from pathlib import Path

import toml

from .static import KILOBYTE, MEGABYTE, ALLOWED_CHUNK_SIZES


class PackagePath:
    """ Extends pathlib.Path adding some commonly used utility methods."""

    def __init__(self, path: str):
        self.path = Path(path)

    def sha256sum(self) -> str:
        """SHA256 Checksum of the file at self.path."""
        hash_algo = sha256()
        buffer = bytearray(128 * KILOBYTE)
        buffer = memoryview(buffer)

        with open(self.path, "rb", buffering=0) as read_file:
            for chunk in iter(lambda: read_file.readinto(buffer), 0):
                hash_algo.update(buffer[:chunk])
        return hash_algo.hexdigest()

    def exists(self) -> bool:
        """Checks if the file at self.path exists."""
        return self.path.exists()

    def chunk_len(self, chunk_buffer_size: int) -> int:  # TODO: rename count_chunks
        """Counts the amount of buffer_size chunks a file can be divided by."""

        return ceil(len(self) / chunk_buffer_size)

    @property
    def name(self) -> str:
        """Returns the name of the file."""
        return str(self.path.name)

    def __len__(self):
        return self.path.stat().st_size

    def __str__(self):
        return self.name

    def is_dir(self) -> bool:
        """Returns True if the path leads to a directory."""
        return self.path.is_dir()

    def is_file(self) -> bool:
        """Returns True if the path leads to a file."""
        return self.path.is_file()


class FileManifest(metaclass=ABCMeta):
    """Provides basic functionality needed to build a file manifest."""

    def __init__(self, target_path: str, chunk_buffer_size: int, *args, **kwargs):
        self.package_path = PackagePath(target_path)

        if chunk_buffer_size not in ALLOWED_CHUNK_SIZES:
            raise ValueError("{chunk_buffer_size} is not an allowed buffer size.")

        self.chunk_buffer_size = chunk_buffer_size
        self.top_directory = None

        # Optional Stuff
        self.extras = dict()

        self.extras["creation_date"] = str(datetime.now())
        self.extras["comment"] = kwargs.get("comment", None)
        self.extras["created_by"] = kwargs.get("created_by", None)

        self.extras = {
            k: v for k, v in self.extras.items() if v is not None
        }  # removes none values

    def verify(self):
        """Verifies all files in the manifest exist."""
        for file_ in self:
            assert file_.exists()  # TODO: Change to if execption

    def __repr__(self):
        return "\n".join([f"{key} : {value}" for key, value in self.__dict__.items()])


class MultipleFileManifest(FileManifest):
    """Extends FileManifest provides multi-file functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path_list = self.get_paths()
        self.top_directory = self.package_path.name

    def get_paths(self):
        """Returns a list of all the files."""
        paths_list = []
        for directory, _, files in walk(self.package_path.path):
            for file_ in files:
                current_path = PackagePath(f"{directory}/{file_}")
                assert current_path.exists()  # TODO: Change to if exeption
                paths_list.append(current_path)
        return paths_list

    def __iter__(self):
        return iter(self.path_list)


# IDEA Custom Multi File Manifest Class
# Initailly makes a custom named top directory.
# Next, it finds the absolute path to all the choosen files and creates symlinks
# to the files in the custom top directory.
# uses os.walk followlinks=True options to walk symbolic links that resolve to dirs.


class SingleFileManifest(FileManifest):
    """Extends FileManifest provides single file functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return str(self.package_path)

    def __iter__(self):
        return iter([self.package_path])


class ManifestMaker:
    """Factory class provides functions to build a manifest."""

    def create(target_path: str, chunk_buffer_size: int, *args, **kwargs):
        """Creates file manifest from the target_path."""
        path = Path(target_path)

        assert path.exists()  # TODO: Change if exception

        if path.is_dir():
            return MultipleFileManifest(target_path, chunk_buffer_size, *args, **kwargs)

        if path.is_file():
            return SingleFileManifest(target_path, chunk_buffer_size, *args, **kwargs)

    def write(manifest: FileManifest, destination: str, chunk_buffer_size: int):
        """Writes file manifest of files to the destination."""

        manifest.verify()

        header = dict()
        file_list = []
        master_hash = ""

        header.update(manifest.extras)
        header["chunk_buffer_size"] = chunk_buffer_size

        if manifest.top_directory:
            header["top_directory"] = manifest.top_directory

        for current_file in manifest:

            manifest = dict()
            manifest["name"] = current_file.name
            manifest["path"] = str(current_file.path)

            file_hash = current_file.sha256sum()
            master_hash += file_hash

            manifest["hash"] = file_hash
            manifest["chunks"] = current_file.chunk_len(chunk_buffer_size)

            file_list.append(manifest)

        header["master_hash"] = master_hash

        destination_path = Path(destination)
        destination_path.touch()

        with open(destination_path, mode="a") as destination_file:
            data = toml.dumps({"header": header})

            destination_file.write(data)
            destination_file.write("\n")

            for file_information in file_list:
                name = file_information.pop("name")
                data = toml.dumps({name: file_information})

                destination_file.write(data)
                destination_file.write("\n")
