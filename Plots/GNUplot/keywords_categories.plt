set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 3.0 butt \
    palfuncparam 2000,0.005 \
    "Helvetica" 30

set size 1.5,1
set title "Topic Categories ".filename."" font "Helvetica,30" 

stats "../Data/".filename using 2 nooutput name 'suitable'
stats "../Data/".filename using 3 nooutput name 'disturbing'

set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 3 spacing 1 width 0 height 0 

set boxwidth 0.9 absolute
set style fill solid 1.00 border lt -1

set style histogram clustered gap 0.5 title textcolor lt -1
set datafile missing '-'
set style data histograms
set ylabel "%"  
set xtics border in scale 0,0 
set xtics norangelimit
set xtics ()
set xrange [ * : *] noreverse writeback
set yrange [ 0 : 50 ] noreverse writeback
set y2range [ * : * ] noreverse writeback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
set grid ytics lt 0 lw 2 lc rgb "#B8B8B8"

set out "../Output/".filename."sentistrength.eps" 

plot "../Data/".filename using (100.*column(2)/suitable_sum):xtic(1) t column(2) lt rgb '#76949F', '' using (100.*column(3)/disturbing_sum):xtic(1) title column(3) lt rgb '#981825'


