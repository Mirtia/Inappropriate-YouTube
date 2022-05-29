set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 3.0 butt \
    palfuncparam 2000,0.005 \
    "Helvetica" 30

set linetype cycle 16
set size 1, 1.3

set style fill solid 1.00 border lt -0.5
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
set style histogram rowstacked title textcolor lt -0.5
set datafile missing '-'
set grid ytics lc rgb '#B8B8B8' lt 0 lw 6
set style data histograms
set xtics border in scale 0,0 nomirror rotate by 90 offset 0, -4.4
set xtics  norangelimit 
set xtics   () 
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "%" 
set yrange [ 0 : 100 ] noreverse writeback
set y2range [ * : * ] noreverse writeback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
set boxwidth 0.8 absolute
set lmargin 10
set bmargin 5

set out "../Output/".filename.".eps"

plot "../Data/".filename using (100.*$2/$17):xtic(1) t column(2), for [i=3:16] '' using (100.*column(i)/column(17)) title column(i)