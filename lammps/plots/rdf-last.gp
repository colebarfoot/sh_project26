set terminal pngcairo size 1200,800
set datafile columnheaders

ices = "7 8"
pairs = "oo oh hh"
temps = "250K 300K 350K 400K 450K 500K"

do for [i in ices] {
    do for [p in pairs] {
        set output p."rdf-overlay".i.".png"
        plot for [t in temps] p."_rdf".i."-".t."-last.txt" u 1:2 w l title t
    }
}
