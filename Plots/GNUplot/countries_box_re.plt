set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 3.0 butt \
    palfuncparam 2000,0.005 \
    "Helvetica" 30

set linetype cycle 16

set style fill solid 1.00 border lt -0.5
set key out
set key font "Helvetica,20"
set key samplen 4 spacing 1 width 0 height 0 
set datafile missing '-'
set grid xtics lc rgb '#B8B8B8' lt 0 lw 1
set xtics 0, 10, 100 font "Helvetica,20"
set ytics norangelimit 
set xlabel "%" offset 0,-0.5
set xrange [ 0 : 100 ] noreverse writeback
set yrange [:] reverse
set lmargin 8.5
set rmargin 10
set style fill solid 1.0

set out "../Output/".filename.".eps"

plot for [col=2:16] "../Data/".filename u col:0: \
    (total=(sum [i=2:16] column(i)),(sum [i=2:col-1] column(i)/total*100)): \
    ((sum [i=2:col] column(i))/total*100): \
    ($0 - 0.8/2.):($0 + 0.8/2.):ytic(1) w boxxyerror ti columnhead(col)
# plot filename using (100.*$2/$17):xtic(1) t column(2), for [i=3:16] '' using (100.*column(i)/column(17)) title column(i)