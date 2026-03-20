set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

ices = "7 8"
pairs = "oo oh hh"
temps = "250K 300K 350K 400K 450K 500K"

ylabel_for(pair) = \
    pair eq "oo"    ? "$g_{\\mathrm{OO}}(r)$"    : \
    pair eq "oh"    ? "$g_{\\mathrm{OH}}(r)$"    : \
    pair eq "hh"    ? "$g_{\\mathrm{HH}}(r)$"    : pair

do for [i in ices] {
    do for [p in pairs] {
        set output p."rdf-overlay".i.".tex"
        set xlabel "$r$ / \\AA"
        set ylabel ylabel_for(p)
        set key outside right

        plot for [t in temps] p."_rdf".i."-".t."-last.txt" using 1:2 with lines title t
    }
}
