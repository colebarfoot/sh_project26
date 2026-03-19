set terminal pngcairo size 1200,800
set datafile columnheaders

files = system("ls last[0-9].txt")

ycols = "Press Volume TotEng Enthalpy HBONDS HMSD OMSD HVACF OVACF BoxRatio"

ylabel_for(col) = \
    col eq "Press"    ? "Pressure (atm)"        : \
    col eq "Volume"   ? "Volume (Å³)"           : \
    col eq "TotEng"   ? "Total Energy (kcal/mol)": \
    col eq "Enthalpy" ? "Enthalpy (kcal/mol)"   : \
    col eq "HBONDS"   ? "Hydrogen Bonds"         : \
    col eq "HMSD"     ? "H MSD (Å²)"            : \
    col eq "OMSD"     ? "O MSD (Å²)"            : \
    col eq "HVACF"    ? "H VACF"                : \
    col eq "OVACF"    ? "O VACF"                : \
    col eq "BoxRatio" ? "Box Ratio"             : col

do for [ycol in ycols] {
    set output ycol.".png"
    set xlabel "Temp"
    set ylabel ycol
    set key outside right
    
    if (ycol eq "HMSD" || ycol eq "OMSD" || ycol eq "BoxRatio") {
        set xrange[250:510]

        plot for [f in files] f using "Temp":ycol with lines \
            title system("basename ".f." .txt | sed 's/^last//'")
    } else {
        set xrange[*:*] 

        if (ycol eq "Press" || ycol eq "Volume" || ycol eq "OVACF" || ycol eq "HVACF") {
            plot for [f in files] f using "Temp":ycol every 5 smooth csplines with lines \
                title system("basename ".f." .txt | sed 's/^last//'")
        } else {
            plot for [f in files] f using "Temp":ycol smooth csplines with lines \
                title system("basename ".f." .txt | sed 's/^last//'")
        }
    }
}
