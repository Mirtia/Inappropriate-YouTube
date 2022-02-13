set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 2.0 butt \
    palfuncparam 2000,0.003 \
    "Helvetica" 30


set key invert reverse Left outside
set key autotitle columnheader

set yrange [0:100]
set ytics 0, 10 , 100
set for [i=10:100:10] ytics 
set grid ytics lc rgb '#B8B8B8' lt 0 lw 6
set xtics rotate by 90 right
set ylabel "%" 
set style data histogram 
set style histogram rowstacked   
set style fill solid border -1
set boxwidth 0.8
set x2label "Email availability" 


set out filename.".eps"

set lmargin 10
set bmargin 5

plot filename using (100*$2/($2+$3)):xtic(1) lt rgb "#76949F" title "True"\
   ,'' using (100*$3/($2+$3))  lt rgb '#981825' title "False"\