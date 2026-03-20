#!/home/s2471548/src/sh-project/venv/bin/python3.12
"""
file: data_analysis.py
author: Cole Barfoot
date: 18-03-2026
python script to analyse parsed thermo data and rdf 
data from lammps simulations
"""
import os
import sys
import getopt
import numpy as np
from scipy.interpolate import CubicSpline, interp1d
from scipy.integrate import quad

# constants !
k = 1.380649e-23
pi = np.pi
o_mass = 16.0
h_mass = 1.0
water_mass = o_mass + 2 * h_mass
nA = 6.02e23

atm_pa = 101325
ang3_m3 = 1e-30
kcal_j = 4184
angfs_cms = 1e7
jmol_evatom = 0.00001036

# get cli options !
if len(sys.argv) == 1:
    raise ValueError("not enough cmdline args")

helpmessage = """
data parser for lammps thermo and rdf files 

-----------------------------------------------------

usage:
    -h, --help      display this help message
    -v, --verbose   display extra info
    -g, --gibbs     do gibbs free energy calculation
                    (computationally intensive)
    -k, --keys      specify keys for time averaged
                    quantities [key1 key2 key3 ...]
    -l, --last      do time averages for last 100000
                    steps
    -s, --startstop specify start and stop of time
                    averaging [start,stop]
    -r, --rdf       specify timestep and pair type 
                    for rdf or cdf plot
                    [timestep,pair_type]
    -c, --cutoff    specify cutoff distance for two 
                    body excess entropy integral
    -p, --phonon    return vacf between [start, stop]

    notes:
    rdf and time averages may be done simultaneously
    if keys or phonon specified then '--startstop' or 
    '--last' must also be used
    if --last flag specified then start, stop ignored
"""

longopts=['help', 
          'verbose', 
          'gibbs',
          'ice=', 
          'keys=', 
          'last',
          'startstop=', 
          'rdf=',
          'cutoff=',
          'phonon',
          ]
args = sys.argv[1:]
opts, args = getopt.getopt(args, 'hvgi:k:ls:r:c:p', longopts=longopts)

# parse cli
verbose = cli_gibbs = cli_avg = cli_rdf = cli_last = cli_ice8 = cli_phonon = False
cli_keys = []
cli_start = cli_stop = cli_timestep = cli_pair_type = 0
cli_cutoff = 20
for opt, arg in opts:
    if opt in ('-h', '--help'):
        print(helpmessage)
        sys.exit()
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-g', '--gibbs'):
        cli_gibbs = True
    elif opt in ('-i', '--ice'):
        if arg == '7' or arg == '7p':
            nmols = 2000
        elif arg == '8':
            nmols = 1728
            cli_ice8 = True
        else:
            print(f"unknown option: ice {arg}")
            sys.exit(1)
    elif opt in ('-k', '--keys'):
        if arg == '':
            print("no keys supplied")
            sys.exit(1)
        cli_keys.append(arg)
        while len(args) > 1:
            cli_keys.append(args.pop(0))
    elif opt in ('-l', '--last'):
        cli_last = True
    elif opt in ('-s', '--startstop'):
        try:
            cli_start, cli_stop = arg.split(',')
        except ValueError as err:
            print(f"startstop not formatted correctly: {err}")
            sys.exit(1)
    elif opt in ('-r', '--rdf'):
        cli_rdf = True
        try:
            cli_timestep, cli_pair_type = arg.split(',')
        except ValueError as err:
            print(f"rdf not formatted correctly: {err}")
            sys.exit(1)
    elif opt in ('-c', '--cutoff'):
        try:
            cli_cutoff = int(arg)
        except ValueError as err:
            print(f"cutoff not formatted correctly: {err}")
            sys.exit(1)
    elif opt in ('-p', '--phonon'):
        cli_phonon = True
    else:
        print(f"unknown option: {opt}")
        sys.exit(1)

if cli_keys:
    cli_avg = True

# specify required options
if 'nmols' not in globals():
    print("type of ice required")
    sys.exit(1)

# get filename from positional args
if len(args) > 1:
    print("too many arguments")
    sys.exit(1)
thermo_file = os.path.abspath(args[0])
file_number = os.path.basename(thermo_file).split('-')[2]
rdf_file = os.path.dirname(thermo_file) + f"/../rdf/{file_number}rdf.dat"
rdf_file = os.path.abspath(rdf_file)

# suppress errors unless verbose
stderr=False
if verbose:
    print(f"thermo file: {thermo_file}")
    print(f"rdf file: {rdf_file}")
    stderr=True
    if cli_keys:
        print(f"keys: {cli_keys}")
    if cli_rdf:
        print(f"rdf: {cli_timestep} {cli_pair_type}")
if not stderr:
    sys.stderr = open(os.devnull, 'w')

# thermodynamic data 
class Thermo:
    def __init__(self, file, gibbs=False, cutoff=20):
        # temp : kelvin
        # press : giga pascals
        # volume : ang3 / atom
        # energy : ev_atom
        # velocity : cm s-1
        # hbonds : per atom
        # c/a : divide by sqrt 2 for ice 8
        
        # simulation system data
        self.mass = nmols * water_mass
        self.natom = nmols*3
        
        self.ice8 = False
        if nmols == 1728:
            self.ice8 = True

        self.n = self.natom/nA
        
        # get data
        self.file = file
        self.keys = None
        self.thermo = {}
        self.thermo_parse()
    
        # intermediate unit conversions
        self.thermo['Press'] *= atm_pa
        self.thermo['TotEng'] *= kcal_j
        self.thermo['Volume'] *= ang3_m3
        self.thermo['OVACF'] *= angfs_cms
        self.thermo['HVACF'] *= angfs_cms

        self.enthalpy()

        self.cutoff = cutoff
        if gibbs:
            self.rdf = RDF(rdf_file)
            self.gibbs()
            self.thermo['Gibbs'] *= jmol_evatom/self.natom
        
        # final unit conversions
        self.thermo['TotEng'] *= jmol_evatom/self.natom
        self.thermo['Enthalpy'] *= jmol_evatom/self.natom
        self.thermo['Press'] /= 1e9
        self.thermo['Volume'] /= ang3_m3 * self.natom
        self.thermo['HBONDS'] /= self.natom

        if cli_ice8:
            self.thermo['BoxRatio'] /= np.sqrt(2)
        
    def thermo_parse(self) -> None:
        data = []
        with open(self.file, 'r') as f:
            # structured data so don't worry too much
            # about this parser being bomb-proof
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
        
        # return data as a dictionary of numpy arrays
        # with thermo quantities as keys
        arr = np.array(data, dtype=np.float64)
        self.thermo = dict(zip(self.keys, arr))

    def enthalpy(self) -> None:
        U = self.thermo['TotEng']
        P = self.thermo['Press']
        V = self.thermo['Volume']
        
        # convert PV to molar quantity before summing
        # with energy in J/mol
        self.thermo['Enthalpy'] = U + (P * V) / self.n

    def change_cutoff(self, newval):
        self.cutoff = newval

    def gibbs(self) -> None:
        T = self.thermo['Temp']
        H = self.thermo['Enthalpy']
        self.thermo['Gibbs'] = H - T * self.entropy()

    def entropy(self):
        dens = self.thermo['Volume']/self.mass
        
        interp = self.rdf.interpolate
        cutoff = self.cutoff
        maxstep = np.max(self.thermo['Timestep'])
        
        sOO, sOH, sHH = [], [], []
        for timestep in self.thermo['Timestep']:
            gOO, _, _ = interp(timestep, 'OO_rdf')
            gOH, _, _ = interp(timestep, 'OH_rdf')
            gHH, _, _ = interp(timestep, 'HH_rdf')
            sOO.append(quad(self.s2, 0, cutoff, args=(gOO,))[0])
            sOH.append(quad(self.s2, 0, cutoff, args=(gOH,))[0])
            sHH.append(quad(self.s2, 0, cutoff, args=(gHH,))[0])
            pct = timestep/maxstep * 100
            if verbose:
                print(f"\rentropy calculation: {pct:.1f}%", end="", flush=True)
        
        if verbose:
            print("")

        sOO = np.array(sOO)
        sOH = np.array(sOH)
        sHH = np.array(sHH)

        return -2 * pi * dens * k * (sOO + sOH + sHH)

    def s2(self, x, g_r):
        return (g_r(x) * np.log(g_r(x)) - g_r(x) + 1) * (x**2)

    def time_average(self, keys, start, stop):
        return {
            key: (np.average(self.thermo[key][start:stop]),\
                    np.std(self.thermo[key][start:stop]))
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
        self.interp_type = 'linear'

    def parse(self):
        step_data = []
        data = []
        numkeys = len(self.keys)
        with open(self.file, 'r') as f:
            # also structured data so don't
            # worry about edge cases
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
        if timestep == "last":
            timestep = self.timesteps[-2]
        elif timestep == "first":
            timestep = self.timesteps[0]

        try:
            timestep = np.float64(timestep)
        except ValueError as err:
            print(f"timestep is not a number: {err}")
            sys.exit(1)

        if pair_type not in self.keys:
            print("unknown pair type")
            sys.exit(1)
        if timestep not in self.timesteps:
            print("invalid timestep")
            sys.exit(1)

        step = str(int(timestep))
        step_data = self.rdf[step]
        x = step_data['distance']
        y = step_data[pair_type]
        xrange = (x.min(), x.max())
        yrange = (y.min(), y.max())
        
        # smooth data
        if self.interp_type == 'spline':
            f1 = CubicSpline(x,y)
        elif self.interp_type == 'linear':
            f1 = interp1d(x,y,kind='linear')
        else: 
            print(f"unknown option: {self.inter_type}")
            sys.exit(1)

        return f1, xrange, yrange

    def interp_type(self, new_type):
        self.interp_type = new_type

def main():
    global cli_keys, cli_start, cli_stop, cli_gibbs, cli_cutoff, \
            cli_last, cli_avg, cli_rdf, cli_phonon 

    thermo_data = Thermo(thermo_file, gibbs=cli_gibbs, cutoff=cli_cutoff)
    timesteps = thermo_data.thermo['Timestep']
    
    if cli_last:
        cli_stop = timesteps[-1]
        cli_start = cli_stop - 100000
    else:
        cli_start = np.float64(cli_start)
        cli_stop = np.float64(cli_stop)

    # do time averaging
    if cli_avg:
        if not cli_keys or not cli_start or not cli_stop: 
            print("keys and startstop not correct")
        
        try:
            start = np.where(timesteps == cli_start)[0][0]
            stop = np.where(timesteps == cli_stop)[0][0]
        except IndexError as err:
            print("timestep not in range")

        avgs = thermo_data.time_average(cli_keys, start, stop)
        for key in cli_keys:
            avg, std = avgs[key]
            print(f"{avg} {std} ", end="")
        print("")
   
    # do rdf
    if cli_rdf:
        if not cli_timestep or not cli_pair_type:
            print("timestep and pair type not specified")

        timestep = cli_timestep

        rdf_data = RDF(rdf_file)

        g_r, xrange, yrange = rdf_data.interpolate(timestep, cli_pair_type)
        xinterp = np.linspace(*xrange, num=1000)
        yinterp = g_r(xinterp)

        print(f"Distance RDF")
        for x, y in zip(xinterp, yinterp):
            print(f"{x} {y}")

    if cli_phonon:
        if not cli_start or not cli_stop: 
            print("startstop not correct")

        try:
            start = np.where(timesteps == cli_start)[0][0]
            stop = np.where(timesteps == cli_stop)[0][0]
        except IndexError as err:
            print("timestep not in range")

        hvacf, ovacf = [], []
        for step in timesteps[start:stop]:
            step = int(step/1000)
            hvacf.append(thermo_data.thermo['HVACF'][step])
            ovacf.append(thermo_data.thermo['OVACF'][step])

        print("Timestep OVACF HVACF")
        for step, cvo, cvh in zip(timesteps[start:stop], ovacf, hvacf):
            print(f"{step} {cvo} {cvh}")
    
if __name__ == "__main__":
    main()
