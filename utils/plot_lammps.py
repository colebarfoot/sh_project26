#!/home/s2471548/src/sh-project/venv/bin/python3.12

import os
import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt

output_dir = "/home/s2471548/src/sh-project/lammps/ice_viii/.out/"
os.makedirs(output_dir, exist_ok=True)


class ThermoData:
    def __init__(self, file, xparam, yparam):
        jobid = file.split("-")[0]
        self.figname = jobid + "-" + yparam + "Vs" + xparam
        self.xdata = []
        self.ydata = []
        with open(file, "r") as f:
            self.lines = f.readlines()
            col_nums = [0, 0]
            for name in (names := self.lines[1].split(" ")):
                if name == xparam:
                    col_nums[0] = names.index(name)
                elif name == yparam:
                    col_nums[1] = names.index(name)
            for line in self.lines[2:]:
                data = line.split(" ")
                self.xdata.append(data[col_nums[0]])
                self.ydata.append(data[col_nums[1]])
            if all(num is None for num in col_nums):
                raise ValueError

    def line_plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.xdata, self.ydata)
        fig.set(figheight=6, figwidth=8)
        plt.savefig(output_dir + self.figname)


def opts():
    file = None
    xparam = None
    yparam = None
    argv = sys.argv[1:]

    opts, _ = getopt.getopt(argv, "f:x:y:")

    for opt, arg in opts:
        if opt == "-f":
            file = arg
        elif opt == "-x":
            xparam = arg
        elif opt == "-y":
            yparam = arg

    if any(x is None for x in (file, xparam, yparam)):
        raise ValueError

    return file, xparam, yparam


thermo_data = ThermoData(*opts())
thermo_data.line_plot()
