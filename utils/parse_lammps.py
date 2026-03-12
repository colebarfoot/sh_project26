#!/home/s2471548/src/sh-project/venv/bin/python3.12
"""
date: 28-01-2026
author: Cole Barfoot
python script to parse thermodynamic output from
default LAMMPS log files and write into plain 
text data file
"""
import os
import sys
import getopt
import datetime

class Lammps:
    def __init__(self, file, cutoff=10):
        self.file = file
        self.data = []
        self.params = []
        
        # isolate thermodynamic output
        with open(file, "r") as f:
            self.lines = f.readlines()
            while self.parse():
                continue
        
        # remove thermo after <cutoff> number of steps
        self.step_cutoff(cutoff)

    def parse(self) -> bool:
        last = self.lines[-1]
        for i, line in enumerate(self.lines):
            if line.strip().startswith("Step"):
                self.lines = self.lines[i:]
                break
            if line == last:
                return False
        if not self.params:
            for name in self.lines[0].strip().split():
                self.params.append(name)
                self.data.append([])
        for j, line in enumerate(self.lines[1:], start=1):
            data_pts = line.strip().split()
            if not data_pts:
                continue
            try:
                float(data_pts[0])
            except ValueError:
                self.lines = self.lines[j:]
                break
            for i in range(len(self.params)):
                try:
                    self.data[i].append(data_pts[i])
                except IndexError:
                    print('malformed line')
                    return False
                if line == last:
                    return False
        return True

    def step_cutoff(self, cutoff):
        if not cutoff > 0:
            raise ValueError
        index = 0
        try:
            for idx, step in enumerate(self.data[0]):
                if int(step) >= cutoff:
                    for i in range(len(self.params)):
                        self.data[i] = self.data[i][idx:]
                    return
        except IndexError:
            print(self.file)
            return
        raise ValueError("too few steps")

def opts():
    cutoff = 10
    argv = sys.argv[1:]
    
    # get cmdline options
    opts, args = getopt.getopt(argv, "c:")

    for opt, arg in opts:
        if opt in ("-c"):
            try:
                cutoff = int(arg)
            except ValueError:
                raise ValueError("cutoff must be an integer")

    if len(args) > 1:
        raise ValueError("only parse one file at a time")
    file = args[0]

    return file, cutoff

file, cutoff = opts()

lammps = Lammps(file, cutoff)

in_dir = os.path.dirname(file)
output_dir = os.path.join(in_dir, "parsed")
os.makedirs(output_dir, exist_ok=True)

input_file = os.path.basename(file)
job_id, _ = os.path.splitext(input_file)
output_file = job_id + "-parsed.txt"
output_file = os.path.join(output_dir, output_file)

with open(output_file, "w") as f:
    f.write(f"# {datetime.date.today()}        " + f"jobid: {job_id}\n")
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

print(f"file: {output_file} parsed")
