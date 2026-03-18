#!/home/s2471548/src/sh-project/venv/bin/python3.12
"""
file: data_analysis.py
author: Cole Barfoot
date: 18-03-2026
python script to analyse sh data
"""
import os
import sys
import getopt
import numpy as np
from scipy.interpolate import CubicSpline, interp1d
from scipy.integrate import quad
import matplotlib.pyplot as plt

# constants !
k = 1.380649e-23
pi = np.pi
o_mass = 16.0
h_mass = 1.0
water_mass = o_mass + 2 * h_mass
nA = 6.02e23

atm_pa = 101325
ang3_cm3 = 1e-30
kcal_j = 4184
angfs_cms = 1e7
jmol_evatom = 0.00001036

if len(sys.argv) == 1:
    raise ValueError("not enough cmdline args")

helpmessage = "takes one argument"
verbose = False

opts, args = getopt.getopt(sys.argv[1:], 'hvi:', longopts=['help', 'verbose', 'ice='])

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print(helpmessage)
        sys.exit()
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-i', '--ice'):
        if arg == '7':
            nmols = 2000
        elif arg == '8':
            nmols = 1728
        else:
            print(f"unknown option: ice {arg}")
            sys.exit()
    else:
        raise ValueError(f"unknown option: {opt}")
if 'nmols' not in globals():
    print("type of ice required")
    sys.exit(1)

if not isinstance(args, list):
    args = [args]
if len(args) > 1:
    print("too many arguments")
    sys.exit(1)
thermo = os.path.abspath(args[0])
job_no = os.path.basename(thermo).split('-')[2]
rdf = os.path.dirname(thermo) + f"/../rdf/{job_no}rdf.dat"
rdf = os.path.abspath(rdf)

if verbose:
    print(f"thermo file: {thermo}")
    print(f"rdf file: {rdf}")

class Thermo:
    def __init__(self, file, gibbs=False, units='real', *args):
        # temp : kelvin
        # press : pascals
        # volume : m3
        # energy : ev_atom
        # velocity : cm s-1

        self.file = file
        self.keys = None
        self.thermo = {}

        self.mass = nmols * water_mass
        self.natom = nmols*3
        self.n = self.natom/nA

        self.thermo_parse()
    
        # intermediate unit conversions
        self.thermo['Press'] *= atm_pa
        self.thermo['TotEng'] *= kcal_j
        self.thermo['Volume'] *= ang3_cm3
        self.thermo['OVACF'] *= angfs_cms
        self.thermo['HVACF'] *= angfs_cms

        self.enthalpy()

        self.cutoff = 20
        if gibbs:
            self.rdf = RDF(rdf)
            self.gibbs()
            self.thermo['Gibbs'] *= jmol_evatom/self.natom
        
        # final unit conversions
        self.thermo['TotEng'] *= jmol_evatom/self.natom
        self.thermo['Enthalpy'] *= jmol_evatom/self.natom
        

    def thermo_parse(self) -> None:
        data = []
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                parts = line.split()

                if line.startswith('#'):
                    comment = i
                    continue
                elif i == (comment+1):
                    self.keys = parts
                    numcols = len(self.keys)
                    data = [[] for _ in range(numcols)]
                    continue

                step = int(parts[0])
                if step == 0 or step % 1000:
                    continue
                for i, num in enumerate(parts):
                    data[i].append(num)

        arr = np.array(data, dtype=np.float64)
        self.thermo = dict(zip(self.keys, arr))

    def enthalpy(self) -> None:
        U = self.thermo['TotEng']
        P = self.thermo['Press']
        V = self.thermo['Volume']
        self.thermo['Enthalpy'] = U + (P * V) / self.n

    def change_cutoff(self, newval):
        self.cutoff = newval

    def entropy(self):
        dens = self.thermo['Volume']/self.mass
        print(len(dens))
        
        interp = self.rdf.interpolate
        cutoff = self.cutoff
        maxstep = np.max(self.thermo['Timestep'])
        
        sOO = sOH = sHH = []
        for timestep in self.thermo['Timestep']:
            gOO, _, _ = interp(timestep, 'OO_rdf')
            gOH, _, _ = interp(timestep, 'OH_rdf')
            gHH, _, _ = interp(timestep, 'HH_rdf')
            sOO.append(quad(self.s2, 0, cutoff, args=(gOO))[0])
            sOH.append(quad(self.s2, 0, cutoff, args=(gOH))[0])
            sHH.append(quad(self.s2, 0, cutoff, args=(gHH))[0])
            pct = timestep/maxstep * 100
            print(f"\rentropy calculation: {pct:.1f}%", end="", flush=True)
        
        print("\nentropy calculation complete !")

        sOO = np.array(sOO)
        sOH = np.array(sOH)
        sHH = np.array(sHH)

        return -2 * pi * dens * k * (sOO + sOH + sHH)

    def gibbs(self) -> None:
        T = self.thermo['Temp']
        H = self.thermo['Enthalpy']
        self.thermo['Gibbs'] = H - T * self.entropy()

    def s2(self, x, g_r):
        return (g_r(x) * np.log(g_r(x)) - g_r(x) + 1) * (x**2)

    def time_average(self, keys, start, stop):
        return {
            key: np.average(self.thermo[key][start:stop])
            for key in keys
        }

class RDF:
    def __init__(self, file, *args):
        self.file = file
        self.keys = [
                'distance', 
                'OO_rdf', 
                'OO_cdf', 
                'OH_rdf', 
                'OH_cdf', 
                'HH_rdf', 
                'HH_cdf'
                ]
        self.rdf = {}
        self.timesteps = []
        self.parse()
        self.interp_type = 'spline'

    def parse(self):
        step_data = []
        data = []
        numkeys = len(self.keys)
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue

                parts = line.split()

                if len(parts) == 2:
                    self.timesteps.append(parts[0])
                    if data:
                        arr = np.array(data, dtype=np.float64)
                        data_dict = dict(zip(self.keys, arr))
                        step_data.append(data_dict)
                    data_dict = {}
                    data = [[] for _ in range(numkeys)]
                    continue

                for j, num in enumerate(parts[1:], start=0):
                    data[j].append(num)
        
        self.rdf = dict(zip(self.timesteps, step_data))    
        self.timesteps = np.array(self.timesteps, dtype=np.float64)

    def interpolate(self, timestep, pair_type):
        if pair_type not in self.keys:
            print("unknown pair type")
            sys.exit(1)
        if timestep not in self.timesteps:
            print(timestep)
            print(self.timesteps)
            print("invalid timestep")
            sys.exit(1)
        
        step = str(int(timestep))
        step_data = self.rdf[step]
        x = step_data['distance']
        y = step_data[pair_type]
        xrange = (x.min(), x.max())
        yrange = (y.min(), y.max())
        
        if self.interp_type == 'spline':
            f1 = CubicSpline(x,y)
        elif self.interp_type == 'linear':
            f1 = interp1d(x,y,kind='linear')
        else: 
            print("unknown option")
            sys.exit(1)

        return f1, xrange, yrange

    def interp_type(self, new_type):
        self.interp_type = new_type

def main():
    thermo_data = Thermo(thermo)
    timesteps = thermo_data.thermo['Timestep']

    mykeys = ['Temp','Press', 'TotEng', 'Volume','Enthalpy','HBONDS']

    step_range = (100000, 500000)
    start, stop = step_range
    start = np.where(timesteps == start)[0][0]
    stop = np.where(timesteps == stop)[0][0]
    
    print(thermo_data.time_average(mykeys, start, stop))

if __name__ == "__main__":
    main()
