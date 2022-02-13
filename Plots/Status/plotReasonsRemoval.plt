set terminal postscript enhanced eps color defaultplex \
   leveldefault \
   dashed dashlength 2.0 linewidth 3.0 butt \
   palfuncparam 2000,0.003 \
   "Helvetica" 45

stats filename using 2 nooutput name 'file'  
set size 3,1.5
set format x '%g%%'

# set ylabel "Reasons" offset 5
set xlabel "Percentage" offset 5

set xrange [0 : 15]
set xtics 0, 5, 100
set style fill solid 1.00 border lt -1
set ytics border in scale 0,0 

set grid xtics lt 0 lw 2 lc rgb "#B8B8B8"

set lmargin 45

set style textbox opaque border 
set out  filename.".eps"




# set title "{/:Bold Reasons why suitable channels got terminated by YouTube platform}" font "Helvetica,50" offset -26


plot filename using ($3*0.5):0:($3*0.5):(0.4):yticlabels(1) lt rgb "#981825" with boxxyerrorbars t '' 
