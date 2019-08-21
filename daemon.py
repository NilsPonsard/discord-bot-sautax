#!/usr/bin/python3
from subprocess import Popen
import sys

python_executable = "python3"
filename = " serveur.py"
found_python = True
try:
    p = Popen(python_executable + filename, shell=True)
    p.wait()
except:
    python_executable = "python"
    try:
        p = Popen(python_executable + filename, shell=True)
        p.wait()
    except:
        print("Unable to find a python executable with discord.py installed you may change the python_executable variable in the daemon.py script")
        found_python = False

while found_python:
    print("\nStarting " + filename)
    p = Popen(python_executable + filename, shell=True)
    p.wait()
