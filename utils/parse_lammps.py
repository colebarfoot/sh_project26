#!/home/s2471548/src/sh-project/venv/bin/python3.12

import os
import sys
import getopt
import datetime

output_dir = "/home/s2471548/src/sh-project/lammps/ice_viii/.out/"
os.makedirs(output_dir, exist_ok=True)


class Lammps:
    def __init__(self, file, *args):
        if len(args) == 0:
            raise ValueError
        self.params = args
        self.data = []
        for _ in self.params:
            self.data.append([])

        with open(file, "r") as f:
            self.lines = f.readlines()
            while self.parse():
                continue

    def parse(self) -> bool:
        for line in self.lines:
            if line.startswith("Total wall time"):
                return False
            if line.startswith("   Step"):
                line_idx = self.lines.index(line)
                self.lines = self.lines[line_idx:]
                break
        col_nums = []
        for name in (names := self.lines[0].strip().split()):
            if any(param == name for param in self.params):
                # potential error if one occurs twice
                col_nums.append(names.index(name))
        if len(col_nums) != len(self.params):
            # does not show which does not exist
            raise ValueError(f"Unknown parameters: {self.params}")
        for line in self.lines[1:]:
            data_pts = line.strip().split()
            if data_pts[0] == ("Loop"):
                line_idx = self.lines.index(line)
                self.lines = self.lines[line_idx:]
                break
            for nums in col_nums:
                nums_idx = col_nums.index(nums)
                self.data[nums_idx].append(data_pts[nums])
        return True


def opts():
    file = None
    params = []
    argv = sys.argv[1:]

    opts, args = getopt.getopt(argv, "f:p:", ["--file", "--params"])

    for opt, arg in opts:
        if opt in ("-f", "--file"):
            file = arg
        elif opt in ("-p", "--file"):
            params.append(arg)
            for param in args:
                params.append(param)

    if file is None:
        raise ValueError
    if params == []:
        raise ValueError

    return file, params


file, params = opts()
jobid = file.split("/")[-1].split(".")[0]
lammps = Lammps(file, *params)
output_file = output_dir + jobid + "-parsed.txt"


with open(output_file, "w") as f:
    f.write(f"{datetime.date.today()}\t" + f"jobid: {jobid}\n")
    for param in params:
        f.write(f"{param} ")
    f.write("\n")
    for i in range(len(lammps.data[0])):
        for j in range(len(params)):
            f.write(f"{lammps.data[j][i]} ")
        f.write("\n")
