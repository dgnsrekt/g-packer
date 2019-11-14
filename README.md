# g-packer

Idea for the bitglitter replacement filepacker.

## Start dev environment.

```
$ git clone git@github.com:dgnsrekt/g-packer.git
$ cd g-packer
$ pipenv sync --dev
$ pipenv shell
```

## Run test
After starting the dev environment run.
```
$ pytest
```

## Run test from nox
After starting the dev environment run.
```
$ nox -s tests
```

## Run Example
After starting the dev environment run.
```
In the example.py change target_pack_folder to the 
location you would like to pack.

$ python example.py
```

## Example of manifest.ini contents
```
[header]
creation_date = "2019-11-13 23:27:18.725056"
chunk_buffer_size = 2097152
top_directory = "stuff"
master_hash = "4fc4d2fd7c2f044dddb20db0e6deb9cc65f6c29ee96abc45a87701a805dba8c4a90185d8e8923bc259a3944f4684e40e53af44b9c1160c37ca28ea6cce22c074"

["image.jpg"]
path = "stuff/image.jpg"
hash = "4fc4d2fd7c2f044dddb20db0e6deb9cc65f6c29ee96abc45a87701a805dba8c4"
chunks = 1

["movie.mp4"]
path = "stuff/movie.mp4"
hash = "a90185d8e8923bc259a3944f4684e40e53af44b9c1160c37ca28ea6cce22c074"
chunks = 763
```
