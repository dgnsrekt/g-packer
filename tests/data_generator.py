# flake8: noqa
from os import getrandom, walk
from pathlib import Path
from shutil import rmtree as rmdir
from time import sleep

from faker import Faker

import logme

from progressbar import progressbar

KILOBYTE = 1024
MEGABYTE = KILOBYTE * 1024


@logme.log(name="Fake-File-Generator")
class FakeFileGenerator:
    """Generates fakes files and folders for testing."""

    fake = Faker()

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.root_directory = self.directory / self.random_folder()

    @staticmethod
    def random_folder():
        """Randomly generates a foldername."""
        return FakeFileGenerator.fake.file_name().split(".")[0]

    @staticmethod
    def random_file():
        """Randomly generates a filename."""
        return FakeFileGenerator.fake.file_name()

    def generate_files(self, *, num_directories: int, num_files: int):
        """Creates random files, directories, and sub directories."""
        self.root_directory.mkdir()

        for _ in range(num_directories):
            directory = self.root_directory / self.random_folder()
            directory.mkdir()

            for _ in range(num_files):
                new_file = directory / self.random_file()
                self.logger.debug(f"creating file{new_file}")
                new_file.touch()

    def generate_data(self, file_size: int):
        """Generates random bytes into each file."""
        for directory, _, files in walk(self.root_directory):
            for file_name in files:
                current_file = Path(directory) / file_name
                self.logger.debug(f"writing to file:\n{current_file}")
                for _ in progressbar(range(file_size)):
                    with open(current_file, mode="ab") as write_file:
                        write_file.write(getrandom(size=MEGABYTE))
