from pathlib import Path
from hashlib import sha256
from os import walk
from math import ceil
from abc import ABCMeta
from datetime import datetime

from static import KILOBYTE, MEGABYTE

import toml


class PackagePath:
    def __init__(self, path: str):
        self.path = Path(path)

    def sha256sum(self) -> str:
        hash_ = sha256()
        bytes_ = bytearray(128 * KILOBYTE)
        mv = memoryview(bytes_)

        with open(self.path, "rb", buffering=0) as read_file:
            for n in iter(lambda: read_file.readinto(mv), 0):
                hash_.update(mv[:n])
        return hash_.hexdigest()

    def exists(self):
        return self.path.exists()

    def chunk_len(self, chunk_size: int):
        return ceil(len(self) / chunk_size)

    @property
    def name(self):
        return str(self.path.name)

    def __len__(self):
        return self.path.stat().st_size

    def __str__(self):
        return self.name

    def __repr__(self):
        return "\n".join([f"{key} : {value}" for key, value in self.__dict__.items()])


class FileManifest(metaclass=ABCMeta):
    def __init__(self, target_path: str, *args, **kwargs):
        self.path = PackagePath(target_path)
        self.chunk_size = kwargs.get("chunk_size", MEGABYTE)
        self.top_directory = None

        # Optional Stuff
        self.extras = dict()

        self.extras["creation_date"] = str(datetime.now())
        self.extras["comment"] = kwargs.get("comment", None)
        self.extras["created_by"] = kwargs.get("created_by", None)

        self.extras = {k: v for k, v in self.extras.items() if v is not None}

    def verify(self):
        for file_ in self:
            assert file_.exists()  # TODO: Change to if execption

    def __repr__(self):
        return "\n".join([f"{key} : {value}" for key, value in self.__dict__.items()])


class MultipleFileManifest(FileManifest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path_list = self.get_paths()
        self.top_directory = self.path.name

    def get_paths(self):
        paths_list = []
        for directory, _, files in walk(self.path.path):
            for file_ in files:
                current_path = PackagePath(f"{directory}/{file_}")
                assert current_path.exists()  # TODO: Change to if exeption
                paths_list.append(current_path)
        return paths_list

    def __iter__(self):
        return iter(self.path_list)


class SingleFileManifest(FileManifest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return str(self.path)

    def __iter__(self):
        return iter([self.path])


class Manifest:
    def make(target_path: str, *args, **kwargs):
        path = Path(target_path)

        assert path.exists()  # TODO: Change if exception

        if path.is_dir():
            return MultipleFileManifest(target_path, *args, **kwargs)

        if path.is_file():
            return SingleFileManifest(target_path, *args, **kwargs)

    def create(manifest: FileManifest, destination: str, chunk_size=MEGABYTE):

        manifest.verify()

        header = dict()
        file_list = []

        master_hash = ""

        header.update(manifest.extras)
        header["chunk_size"] = chunk_size

        if manifest.top_directory:
            header["top_directory"] = manifest.top_directory

        for file_ in manifest:

            manifest = dict()
            manifest["name"] = file_.name
            manifest["path"] = str(file_.path)

            _hash = file_.sha256sum()
            master_hash += _hash

            manifest["hash"] = _hash
            manifest["chunks"] = file_.chunk_len(chunk_size)

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


def manny():
    manifest = Manifest.make("logme.ini", comment="hello from earth")
    for x in manifest:
        assert x.exists()
        print(x)
        print(x.path)

    # Manifest.create(manifest, "manifest.init")

    manifest = Manifest.make("stuff", created_by="kevin")
    for x in manifest:
        assert x.exists()
        print(x)
        print(x.path)

    # Manifest.create(manifest, "manifest_single")


def main():
    y = Path("logme.ini")
    x = PackagePath("logme.ini")

    print(y)
    print(y.name)

    print(x)
    print(x.sha256sum())
    print(len(x))
    print(x.chunks_length(chunk_size=MEGABYTE))
