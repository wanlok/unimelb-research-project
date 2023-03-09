import subprocess
import time

if __name__ == '__main__':
    first = True
    while True:
        if not first:
            time.sleep(60 + 3)
        subprocess.Popen(['python', 'crawler_2.py']).wait()
        time.sleep(60 + 3)
        subprocess.Popen(['python', 'crawler_5.py']).wait()
        first = False
