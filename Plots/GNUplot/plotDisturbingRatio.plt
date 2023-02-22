set terminal postscript enhanced eps color defaultplex \
   leveldefault \
   dashed dashlength 2.0 linewidth 3.0 butt \
   palfuncparam 2000, 0.003 \
   "Helvetica" 30

stats filename using 1 nooutput name 'file'

set key bot right
set key samplen 1
set key font ",25"
set grid ytics xtics lt 0 lw 2 lc rgb "#B8B8B8"
set xlabel filename
set ylabel "CDF" offset 2,0
set yrange [0:1]
set xrange[0:*]

set out "../Output/".filename.".eps"

plot "../Data/".filename using 1:(1./file_records) smooth cumulative title "" lw 2 lt rgb "#981825"
