KILOBYTE = 1024
MEGABYTE = KILOBYTE * 1024
ALLOWED_CHUNK_SIZES = [
    KILOBYTE * 256,
    KILOBYTE * 512,
    MEGABYTE * 1,
    MEGABYTE * 2,
    MEGABYTE * 4,
    MEGABYTE * 8,
    MEGABYTE * 16,
]