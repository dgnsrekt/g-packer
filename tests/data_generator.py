# flake8: noqa
from contextlib import contextmanager
from os import getrandom, walk
from pathlib import Path
from shutil import rmtree as rmdir
from time import sleep

from faker import Faker

import logme

from progressbar import progressbar

from .environment import PRE_PROCESS_DATA

KILOBYTE = 1024
MEGABYTE = KILOBYTE * 1024


@logme.log(name="Fake-File-Generator")
class FakeFileGenerator:
    fake = Faker()

    def __init__(self, directory, filesize):  # think about making this a config env var
        self.directory = Path(directory)
        self.file_size = filesize
        self.root_directory = self.directory / self.random_folder()

    @staticmethod
    def random_folder():
        return FakeFileGenerator.fake.file_name().split(".")[0]

    @staticmethod
    def random_file():
        return FakeFileGenerator.fake.file_name()

    def _generate_files(self, directories=2, files=2):  # may get rid of self
        self.root_directory.mkdir()

        for _ in range(directories):
            directory = self.root_directory / self.random_folder()
            directory.mkdir()

            for _ in range(files):
                file_ = directory / self.random_file()
                self.logger.debug(f"creating file{file_}")
                file_.touch()

    def _generate_data(self):
        for directory, _, files in walk(self.root_directory):
            for file_ in files:
                file_ = Path(directory) / file_
                self.logger.info(f"writing to file:\n{file_}")
                for _ in progressbar(range(self.file_size)):
                    with open(file_, mode="ab") as write_file:
                        write_file.write(getrandom(size=MEGABYTE))

    def _clean_up(self):
        self.logger.info(f"cleaning up {self.root_directory}")
        rmdir(self.root_directory.parent.parent)  # TODO: make this better

    def generate(self):
        self._generate_files()
        self._generate_data()

    @contextmanager
    def manager(self):  # this needs to come out and go to the tester
        # both the pre and post should close after running
        try:
            self.generate()
            yield self.root_directory
        finally:
            self._clean_up()


def main():
    fg = FakeFileGenerator(PRE_PROCESS_DATA, 25)
    with fg.manager() as working_directory:
        for x, y, z in walk(working_directory):
            print("procesing...")
            print(x, y, z)
            sleep(1)


if __name__ == "__main__":
    main()
