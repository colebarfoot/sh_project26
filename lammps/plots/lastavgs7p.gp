set terminal pngcairo size 1200,800
set datafile columnheaders

ycols = "Press Volume TotEng Enthalpy HBONDS HMSD OMSD HVACF OVACF BoxRatio"

do for [ycol in ycols] {
    set output ycol."7p.png"
    set xlabel "Temp"
    set ylabel ycol
    set key outside right
    
    if (ycol eq "HMSD" || ycol eq "OMSD" || ycol eq "BoxRatio") { 
    	plot "last7p.txt" using "Temp":ycol with lines title ycol
    } else {
        if (ycol eq "Press" || ycol eq "Volume" || ycol eq "OVACF" || ycol eq "HVACF") {
            plot "last7p.txt" using "Temp":ycol every 5 smooth csplines with lines title ycol
        } else {
            plot "last7p.txt" using "Temp":ycol smooth csplines with lines title ycol
        }
    }
}
