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

