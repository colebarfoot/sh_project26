#
# file: rdf-last.gp
# author: Cole Barfoot
# date: 18-03-2026
# gnuplot script to overlay interpolated rdf data 
# from lammps simulation
#
####################################################

set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

# files and data
ices = "7 8 7p"
pairs = "oo oh hh"
temps = "250K 300K 350K 400K 450K 500K"
ptemps = "450K 500K 540K 600K 650K 680K"

ylabel_for(pair) = \
    pair eq "oo"    ? "$g_{\\mathrm{OO}}(r)$"    : \
    pair eq "oh"    ? "$g_{\\mathrm{OH}}(r)$"    : \
    pair eq "hh"    ? "$g_{\\mathrm{HH}}(r)$"    : pair

do for [i in ices] {
    do for [p in pairs] {
        # configure plot
        set output p."rdf-overlay".i.".tex"
        set xlabel "$r$ / \\AA"
        set ylabel ylabel_for(p)
        set yrange[*:6]
        set grid lw 0.5 lc rgb "#cccccc"
        set key inside right
        
        # random colours !
        if (i eq "7p") {
            plot for [pt in ptemps] p."_rdf".i."-".pt."-last.txt" using 1:2 with lines title pt
        } else {
            plot for [t in temps] p."_rdf".i."-".t."-last.txt" using 1:2 with lines title t
        }
    }
}
