set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

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
    col eq "BoxRatio" ? "$\\frac{c}{a}$"                                     : col

do for [ycol in ycols] {
    set output ycol."7p.tex"
    set xlabel "$T$ / K"
    set ylabel ylabel_for(ycol)
    set key outside right
    stdev = ycol."_std"
    
    if (ycol eq "HMSD" || ycol eq "OMSD" || ycol eq "BoxRatio") { 
        plot file using "Temp":ycol:stdev with yerrorbars notitle, \
             file using "Temp":ycol with points pt 5 ps 0.5 notitle, \
    	     file using "Temp":ycol with lines notitle
    } else {
        if (ycol eq "Press" || ycol eq "Volume" || ycol eq "OVACF" || ycol eq "HVACF") {
            plot file using "Temp":ycol:stdev with yerrorbars notitle, \
                 file using "Temp":ycol with points pt 5 ps 0.5 notitle, \
                 file using "Temp":ycol every 5 smooth csplines with lines notitle
        } else {
            plot file using "Temp":ycol:stdev with yerrorbars notitle, \
                 file using "Temp":ycol with points pt 5 ps 0.5 notitle, \
                 file using "Temp":ycol smooth csplines with lines notitle
        }
    }
}
