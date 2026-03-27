set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

set linetype 1 lc rgb "red"
file = "hmsdvar.txt"
file2 = "hmsdvar-pre.txt"

set xlabel "Timestep / ps"
set ylabel "$\\langle r^2 \\rangle_{\\mathrm{H}}$ / \\AA"
set output "hmsdvar.tex"

set label 1 "440K" at screen 0.02,0.02 left front
plot file every 100 u (column("Timestep")/1000):"HMSD" w l lt 1 notitle,\
     file every 100 u (column("Timestep")/1000):"HMSD" w p pt 5 ps 0.5 lt 1 notitle

unset label 1
set label 2 "430K" at screen 0.02,0.02 left front
set output "hmsdvar-pre.tex"
plot file2 every 100 u (column("Timestep")/1000):"HMSD" w l lt 1 notitle,\
     file2 every 100 u (column("Timestep")/1000):"HMSD" w p pt 5 ps 0.5 lt 1 notitle
