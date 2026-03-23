set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

set linetype 1 lc rgb "blue"
file = "equilib.txt"

set xlabel "Timestep / ps"
set ylabel "$T$ / K"
set output "equilib.tex"

plot file every 10 u (column("Timestep")/1000):"Temp" w l lt 1 notitle,\
     file every 10 u (column("Timestep")/1000):"Temp" w p pt 5 ps 0.5 lt 1 notitle
