set terminal postscript enhanced eps color defaultplex \
   leveldefault \
   dashed dashlength 2.0 linewidth 3.0 butt \
   palfuncparam 2000,0.003 \
   "Helvetica" 30

set boxwidth 0.75 absolute
set style fill   solid 1.00 border lt -1
set grid nopolar
set grid noxtics nomxtics ytics nomytics noztics nomztics nortics nomrtics \
nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics
set grid layerdefault   lt 0 linecolor 0 linewidth 0.500,  lt 0 linecolor 0 linewidth 0.500
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 3 spacing 1 width 0 height 0 
set style histogram rowstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 0,0 nomirror rotate by -270  autojustify
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
NO_ANIMATION = 1

set out "../Output/emotions.eps"

plot "../Data/emotions.dat" using (100.*$2/$10):xtic(1) t column(2) lt rgb '#e30b00', '' using (100.*column(3)/column(10)) title column(3) lt rgb '#ff6d19', \
'' using (100.*column(4)/column(10)) title column(4) lt rgb '#9d3cdf', '' using (100.*column(5)/column(10)) title column(5) lt rgb '#7af64e', \
'' using (100.*column(6)/column(10)) title column(6) lt rgb '#faff39', '' using (100.*column(7)/column(10)) title column(7) lt rgb '#53ccc9', \
'' using (100.*column(8)/column(10)) title column(8) lt rgb '#53cc63', '' using (100.*column(9)/column(10)) title column(9) lt rgb '#c8f92c'
