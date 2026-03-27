
set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

# files and data
ices = "7 8"
atoms = "O H"
temps = "250K 300K 350K 400K 450K 500K"

ycol_for(atom) = \
    atom eq "O"     ? "OVACF"   : \
    atom eq "H"     ? "HVACF"   : atom

ylabel_for(atom) = \
    atom eq "O"    ? "$C_{v_{H}(t)}$"    : \
    atom eq "H"    ? "$C_{v_{O}(t)}$"    : atom

do for [i in ices] {
    do for [atom in atoms] {
        # configure plot
        set output atom."_vacf-overlay".i.".tex"
        set xlabel "$t$ / ps"
        set ylabel ylabel_for(atom)
        set key outside right
        
        # random colours !
        plot for [t in temps] "vacf".i."-".t.".txt" using ($1/1000 - 2990):ycol_for(atom) \
            smooth csplines with lines title t
    }
}
