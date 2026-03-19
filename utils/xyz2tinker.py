#!/usr/bin/python
"""
date: 28-01-2026
author: Cole Barfoot
python script to convert xyz coordinate files generated
by GenIce2 to tinker xyz format
"""
import os
import sys

class xyz:
    def __init__(self, filepath):
        self.filename = os.path.basename(filepath).split(".")[0]
        with open(filepath, "r") as f:
            lines = f.readlines()
            self.num_atoms = int(lines[0])
            self.atom_data = [line.strip().split() for line in lines[2:]]

    def convert_data(self):
        converted_data = []
        for data, i in enumerate(self.atom_data, start=1):
            atomid = data[0]
            new_line = [i, atomid, *data[1:]]
            if atomid == "O":
                atomtype = 1
                bond1 = i + 1
                bond2 = i + 2
                new_line = new_line + [atomtype, bond1, bond2]
            elif atomid == "H":
                atomtype = 2
                if i % 3 == 0:
                    bond1 = i - 2
                else:
                    bond1 = i - 1
                new_line = new_line + [atomtype, bond1]
            converted_data.append(new_line)
        return converted_data

if len(sys.argv) > 1:
    raise ValueError("only convert one file at a time")
input_file = sys.argv[1]
xyz = xyz(input_file)
dirname = os.path.dirname(input_file)
output_file = dirname + xyz_file.filename + ".tinker"

with open(output_file, "w") as f:
    f.write(f"{xyz_file.num_atoms} converted data file\n")
    for data in xyz_file.convert_data():
        i, atomid, x, y, z, atomtype, bond1 = data[:7]
        f.write(f"{i} {atomid} {x} {y} {z} {atomtype} {bond1} ")
        if atomid == "O": 
            f.write(f"{data[7]}") # not all lines are the same length
        f.write("\n")
