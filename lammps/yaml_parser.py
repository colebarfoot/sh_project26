#!/home/s2471548/src/sh-project/venv/bin/python3.12
"""
file: yaml_parser.py
date: 11-03-26
author: Cole Barfoot
script to parse and clean yaml thermo output from 
lammps simulations and create plain text data file 
(adapted from [1]).

[1]: A Set of Tutorials for the LAMMPS Simulation 
     Package [Article v1.0] by Simon Gravelle, 
     Cecilia M. S. Alvares, Jacob R. Gissinger, 
     and Axel Kohlmeyer, 
     published in LiveCoMS, 6(1), 3037 (2025) 
"""

import numpy as np
import re
import yaml
import os
import sys

# do cmdline and file operations
if len(argv) != 2:
    raise ValueError("incorrect usage")
file = sys.argv[1]
filebase = os.path.basename(file)
outdir = "/home/s2471548/src/sh-project/lammps/parsed-data/"
os.makedirs(outdir, exist_ok=True)
parsed = outdir + "parsed-" + filebase

# Import the data from the yaml file
pattern = r"^(keywords:.*$|data:$|---$|\.\.\.$|  - \[.*\]$)"
docs = ""
with open(file) as f:
    for line in f:
        m = re.search(pattern, line)
        if m:
            docs += m.group(0) + "\n"
thermo = list(yaml.load_all(docs, Loader=yaml.CSafeLoader))
nruns = remainder = len(thermo)

# write parsed data to text file
with open(parsed, "w") as f:
    f.write(f"# {datetime.date.today()}        " + f"jobid: {job_id}\n")
    for kword in thermo[1]['keywords']:
        f.write(f"{kword} ")
    f.write("\n")
    while remainder:
        print(nruns - remainder)
        for data in thermo[nruns - remainder]['data']:
            for value in data:
                f.write(f"{value} ")
            f.write("\n")
        remainder -= 1
