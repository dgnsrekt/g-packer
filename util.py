from time import time, sleep


def timeit(method):
    def timed(*args, **kw):
        start = time()
        result = method(*args, **kw)
        end = time()
        seconds = round(end - start)
        print(f"\n{method.__name__} {seconds}s")
        return result

    return timed


@timeit
def main():
    for _ in range(30):
        sleep(0.1)
        print(".", end="", flush=True)


if __name__ == "__main__":
    main()
