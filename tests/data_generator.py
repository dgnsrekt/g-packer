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
    fake = Faker()

    def __init__(self, directory):  # think about making this a config env var
        self.directory = Path(directory)
        self.root_directory = self.directory / self.random_folder()

    @staticmethod
    def random_folder():
        return FakeFileGenerator.fake.file_name().split(".")[0]

    @staticmethod
    def random_file():
        return FakeFileGenerator.fake.file_name()

    def generate_files(self, *, num_directories, num_files):  # may get rid of self
        self.root_directory.mkdir()

        for _ in range(num_directories):
            directory = self.root_directory / self.random_folder()
            directory.mkdir()

            for _ in range(num_files):
                file_ = directory / self.random_file()
                self.logger.debug(f"creating file{file_}")
                file_.touch()

    def generate_data(self, file_size):
        for directory, _, files in walk(self.root_directory):
            for file_ in files:
                file_ = Path(directory) / file_
                self.logger.debug(f"writing to file:\n{file_}")
                for _ in progressbar(range(file_size)):
                    with open(file_, mode="ab") as write_file:
                        write_file.write(getrandom(size=MEGABYTE))
