#
# file: lastavgs7p.gp
# author: Cole Barfoot
# date: 18-03-2026
# gnuplot script to print thermo data from 
# lammps simulations of high-temp, high-pressure
# ice-vii simulations
#
###################################################

set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

# data and labels
file = "last7p.txt"
ycols = "Press Volume TotEng Enthalpy HBONDS HMSD OMSD BoxRatio"

ylabel_for(col) = \
    col eq "Press"    ? "$P$ / GPa"                                          : \
    col eq "Volume"   ? "$V$ / \\AA$^{3}$"                                   : \
    col eq "TotEng"   ? "$E_{\\mathrm{tot}}$ / eV atom$^{-1}$"               : \
    col eq "Enthalpy" ? "$H$ / eV atom$^{-1}$"                               : \
    col eq "HBONDS"   ? "H-Bonds"                                            : \
    col eq "HMSD"     ? "$\\langle r^2 \\rangle_{\\mathrm{H}}$ / \\AA$^{2}$" : \
    col eq "OMSD"     ? "$\\langle r^2 \\rangle_{\\mathrm{O}}$ / \\AA$^{2}$" : \
    col eq "BoxRatio" ? "$c$/$a$"                                     : col

# colours !
set linetype 1 lc rgb "blue"

do for [ycol in ycols] {
    # configure plot and error bars
    set output ycol."7p.tex"
    set xlabel "$T$ / K"
    set ylabel ylabel_for(ycol)
    set key outside right
    set bars small
    set pointintervalbox 0
    stdev = ycol."_std"
    
    if (ycol eq "HMSD" || ycol eq "OMSD" || ycol eq "BoxRatio" || ycol eq "Volume") { 
    	plot file using "Temp":ycol with lines lt 1 notitle, \
             file using "Temp":ycol:stdev with yerrorbars lt 1 pt 5 ps 0.5 notitle
    } else {
        if (ycol eq "Press") {
            plot file using "Temp":ycol:stdev with yerrorbars lt 1 pt 5 ps 0.5 notitle, \
        } else {
            plot file using "Temp":ycol smooth csplines with lines lt 1 notitle, \
                 file using "Temp":ycol:stdev with yerrorbars lt 1 pt 5 ps 0.5 notitle
        }
    }
}
