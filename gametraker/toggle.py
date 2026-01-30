import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
FLAG = os.path.join(BASE, "tracker.flag")

if os.path.exists(FLAG):
    os.remove(FLAG)
else:
    open(FLAG, "w").close()
    subprocess.Popen(
        ["pythonw", "tracker.py"],
        cwd=BASE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
