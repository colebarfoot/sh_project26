#!/home/s2471548/src/sh-project/venv/bin/python3.12

import os
import sys
import getopt
import datetime


class Lammps:
    def __init__(self, file, cutoff=10):
        self.data = []
        self.params = []

        with open(file, "r") as f:
            self.lines = f.readlines()
            while self.parse():
                continue

        self.step_cutoff(cutoff)

    def parse(self) -> bool:
        for i, line in enumerate(self.lines):
            if line.startswith("Total wall time"):
                return False
            if line.strip().startswith("Step"):
                self.lines = self.lines[i:]
                break
        if not self.params:
            for name in self.lines[0].strip().split():
                self.params.append(name)
                self.data.append([])
        for j, line in enumerate(self.lines[1:], start=1):
            data_pts = line.strip().split()
            if not data_pts:
                continue
            if data_pts[0].isalpha():
                self.lines = self.lines[j:]
                break
            if len(data_pts) < len(self.params):
                return False
            for i in range(len(self.params)):
                self.data[i].append(data_pts[i])
            if j == len(self.lines) - 1:
                return False
        return True

    def step_cutoff(self, cutoff):
        if not cutoff > 0:
            raise ValueError
        index = 0
        for step in self.data[0]:
            if int(step) >= cutoff:
                index = self.data[0].index(step)
                for i in range(len(self.params)):
                    self.data[i] = self.data[i][index:]
                return
        raise ValueError("too few steps")


def opts():
    file = None
    cutoff = 10
    argv = sys.argv[1:]

    opts, _ = getopt.getopt(argv, "f:p:c:", ["--file", "--params", "--cutoff"])

    for opt, arg in opts:
        if opt in ("-f", "--file"):
            file = arg
        elif opt in ("-c", "--cutoff"):
            try:
                cutoff = int(arg)
            except TypeError:
                raise Exception

    if file is None:
        raise ValueError

    return file, cutoff


file, cutoff = opts()

lammps = Lammps(file, cutoff)

in_dir = os.path.dirname(file)
output_dir = os.path.join(in_dir, "parsed")
os.makedirs(output_dir, exist_ok=True)

_, file = os.path.split(file)
file, _ = os.path.splitext(file)
output_file = file + "-parsed.txt"
output_file = os.path.join(output_dir, output_file)

with open(output_file, "w") as f:
    f.write(f"{datetime.date.today()}        " + f"jobid: {file}\n")
    for param in lammps.params:
        f.write(f"{param} ")
    f.write("\n")
    for i in range(len(lammps.data[0])):
        for j in range(len(lammps.params)):
            try:
                f.write(f"{lammps.data[j][i]} ")
            except IndexError:
                pass
        f.write("\n")
