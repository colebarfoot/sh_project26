# Modelling Different Forms of Ice

Senior Honours project using LAMMPS molecular dynamics software to model the order/disorder
Ice--VIII $\leftrightarrow$ Ice--VII phase transition, and the high-temperature 
`plastic' Ice-VII phase with the AMOEBA polarizable force field.
Most of the recent development in water pair potentials has been made in successfully integrating
induced dipoles.
AMOEBA ice is as yet untested for high-pressure.

### Aims
---
1. Learn how to use the LAMMPS molecular dynamics software
2. Become proficient with using the SOPA compute cluster to run LAMMPS simulations
3. Do simulations with AMOEBA ice and assess the force field's suitability

### Directory structure
---
*   sh-project/
    *   README
    *   lammps/
        *   lammps input scripts
        *   slurm batch scripts
        *   data analysis tools
        *   plots
    *   report/
        *   sh_report26.tex
        *   mystyle.sty
        *   references.bib
        *   sections/
            *   sections
    *   utils/
        *   general purpose tooling

### Results
---
AMOEBA ice reproduced the VIII $\to$ VII transition, albeit with significant hysteresis.
This is attributed to the difficulty associated with collective reorientations which satisfy the 
ice rules.
Some features appeared at high-pressure and high-temperature which may be indicative of a `plastic' 
phase but this is as yet unconfirmed.
