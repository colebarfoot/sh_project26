set terminal cairolatex pdf standalone size 12cm,8cm color colortext
set datafile columnheaders

set linetype 1 lc rgb "red"
file = "hmsdvar.txt"

set xlabel "Timestep / ps"
set ylabel "$\\langle r^2 \\rangle_{\\mathrm{H}}$ / \\AA"
set output "hmsdvar.tex"
set label "Ice--VIII just above transition temperature" at graph 0.8,0.2 boxed right 

plot file every 100 u (column("Timestep")/1000):"HMSD" w l lt 1 notitle,\
     file every 100 u (column("Timestep")/1000):"HMSD" w p pt 5 ps 0.5 lt 1 notitle
