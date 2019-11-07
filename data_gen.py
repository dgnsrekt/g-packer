from os import walk
from pathlib import Path
from faker import Faker
from testdata import * 
from environment import PRE_PROCESS_DATA 

get_name(name_count=2, as_str=True)

FILE_SIZE = (1024 * 1024)

while True:
    break
    print(fake.file_path())
    print(fake.binary(length=MAX))
    break


class FileGenerator:
    fake = Faker()

    def __init__(self, directory): # think about making this a config env var 
        self.directory = Path(directory)
        self.root_dir = self.directory / self.random_folder()

    @staticmethod
    def random_folder():
        return FileGenerator.fake.file_name().split(".")[0]

    @staticmethod
    def random_file():
        return FileGenerator.fake.file_name()

    def generate_files(self, dirs=2, files=4): # may get rid of self
        self.root_dir.mkdir()

        for _ in range(dirs):
            _dir = self.root_dir / self.random_folder()
            _dir.mkdir()

            for _ in range(files):
                _file = _dir / self.random_file()
                _file.touch()
                #print(_file, "created")

    def generate_data(self, size=0):
        for _dir, _sub, _files in walk(self.root_dir):
            for _file in _files:
                print(_dir, _file)

        
        

fg = FileGenerator(PRE_PROCESS_DATA)
fg.generate_files()
fg.generate_data()





