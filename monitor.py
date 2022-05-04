import os
import time

while True:
    os.system('python run.py')
    os.system("TASKKILL /F /IM firefox.exe")
    time.sleep(15)
