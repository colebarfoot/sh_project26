#
# file: lastavgs.gp
# author: Cole Barfoot
# date: 18-03-2026
# gnuplot script to plot thermo data of lammps
# simulation around the ice-vii/ice-viii phase
# boundary
#
##################################################


set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

# data and columns
files = system("ls last[0-9].txt")
ycols = "Press Volume TotEng Enthalpy HBONDS HMSD OMSD BoxRatio"

ylabel_for(col) = \
    col eq "Press"    ? "$P$ / GPa"                                          : \
    col eq "Volume"   ? "$V$ / \\AA$^{3}$ atom$^{-1}$"                       : \
    col eq "TotEng"   ? "$E_{\\mathrm{tot}}$ / eV atom$^{-1}$"               : \
    col eq "Enthalpy" ? "$H$ / eV atom$^{-1}$"                               : \
    col eq "HBONDS"   ? "H-Bonds / atom"                                     : \
    col eq "HMSD"     ? "$\\langle r^2 \\rangle_{\\mathrm{H}}$ / \\AA$^{2}$" : \
    col eq "OMSD"     ? "$\\langle r^2 \\rangle_{\\mathrm{O}}$ / \\AA$^{2}$" : \
    col eq "BoxRatio" ? "$c$/$a$"                                            : col

# colours ! 
set linetype 1 lc rgb "red"
set linetype 2 lc rgb "black"

do for [ycol in ycols] {
    # configure plot and error bars !
    set output ycol.".tex"
    set xlabel "$T$ / K"
    set ylabel ylabel_for(ycol)
    set bars small
    set pointintervalbox 0
    stdev = ycol."_std"
    
    # smoothing options !
    if (ycol eq "HMSD" || ycol eq "OMSD" || ycol eq "BoxRatio" || ycol eq "Volume") {
        set xrange[250:510]
        set key inside right

        if (ycol eq "HMSD") {
            set key inside left
        }

        plot for [i=1:words(files)] word(files,i) using "Temp":ycol:stdev with yerrorbars lt i pt 5 ps 0.5 notitle, \
             for [i=1:words(files)] word(files,i) using "Temp":ycol with lines lt i \
                title system("basename ".word(files,i)." .txt | sed 's/^last/Ice /'")
    } else {
        set xrange[*:*] 
        set key inside left
        
        if (ycol eq "Press") {
            plot for [i=1:words(files)] word(files,i) using "Temp":ycol:stdev with yerrorbars lt i pt 5 ps 0.5 \
                    title system("basename ".word(files,i)." .txt | sed 's/^last/Ice /'")
        } else {
            plot for [i=1:words(files)] word(files,i) using "Temp":ycol:stdev with yerrorbars lt i pt 5 ps 0.5 notitle, \
                 for [i=1:words(files)] word(files,i) using "Temp":ycol smooth csplines with lines lt i \
                    title system("basename ".word(files,i)." .txt | sed 's/^last/Ice /'")
        }
    }
}
