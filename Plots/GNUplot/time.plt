set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 3.0 butt \
    palfuncparam 2000,0.005 \
    "Helvetica" 30


min(a, b) = (a < b) ? a : b
max(a, b) = (a > b) ? a : b
set size 1.2, 1


set key top left
set key samplen 1
set key font ",25"

stats filename using 2 nooutput name "TimeSuit"
stats filename using 1 nooutput name "CountSuit"
stats filename using 4 nooutput name "TimeDist"
stats filename using 3 nooutput name "CountDist"

set grid ytics xtics lt 0 lw 2 lc rgb "#B8B8B8"
set xrange[min(TimeSuit_min, TimeDist_min) - 1 : max(TimeSuit_max, TimeSuit_min) + 1]
set yrange[0 : max(CountSuit_max, CountDist_max) + 10]

set style data linespoints
set xlabel "Year"
set ylabel "Count"


set out "../Output/".filename.".eps"

plot filename using 2:1 title "Suitable" lw 2 lt rgb "#76949F", \
'' using 4:3 title "Disturbing" lw 2 lt rgb '#981825'
