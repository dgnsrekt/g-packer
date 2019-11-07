import time
import progressbar

for i in progressbar.progressbar(range(100), redirect_stdout=True):
    print("SOME TEST", i)
    time.sleep(0.02)
