#!/usr/bin/python

import os
import sys


class exyz:
    def __init__(self, filepath):
        self.filename = filepath.split("/")[-1].split(".")[0]

        with open(filepath, "r") as f:
            lines = f.readlines()
            self.num_atoms = int(lines[2])
            self.atom_data = [line.strip().split() for line in lines[4:]]

    def convert_data(self):
        converted_data = []

        i = 1
        for data in self.atom_data:
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

            i += 1

        return converted_data


input_file = sys.argv[1]
exyz_file = exyz(input_file)
output_dir = os.path.dirname(input_file)
output_file = output_dir + exyz_file.filename + ".tinker"

with open(output_file, "w") as f:
    f.write(f"{exyz_file.num_atoms} converted data file\n")
    for data in exyz_file.convert_data():
        i, atomid, x, y, z, atomtype, bond1 = data[:7]
        f.write(f"{i} {atomid} {x} {y} {z} {atomtype} {bond1} ")
        if atomid == "O":
            f.write(f"{data[7]}")
        f.write("\n")
