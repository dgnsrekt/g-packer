from pathlib import Path
from hashlib import sha256
from math import ceil


class PackagePath:
    def __init__(self, path: str):
        self.path = Path(path)

    def sha256sum(self) -> str:
        _hash = sha256()
        _bytes = bytearray(128 * 1024)
        mv = memoryview(_bytes)

        with open(self.path, "rb", buffering=0) as read_file:
            for n in iter(lambda: read_file.readinto(mv), 0):
                _hash.update(mv[:n])
        return _hash.hexdigest()

    def chunks_length(self, *, chunk_size: int):
        return ceil(len(self) / chunk_size)

    def __len__(self):
        return self.path.stat().st_size

    def __repr__(self):
        return str(self.path.name)


y = Path("logme.ini")
x = PackagePath("logme.ini")

print(y)
print(y.name)

print(x)
print(x.sha256sum())
print(len(x))
MB = 1024
print(x.chunks_length(chunk_size=MB))
