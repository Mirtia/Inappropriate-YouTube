set terminal postscript enhanced eps color defaultplex \
   leveldefault \
   dashed dashlength 2.0 linewidth 3.0 butt \
   palfuncparam 2000,0.003 \
   "Helvetica" 30


stats "Suitable/".filename using 1 nooutput name 'Users'
stats "Disturbing/".filename using 1 nooutput name 'DisUsers'
# stats "Popular/".filename using 1 nooutput name 'PopUsers'
# stats "Random/".filename using 1 nooutput name 'RandUsers'

set out filename.".eps"

set print "logfile" append
print Users_records ,Users_max ,Users_min ,Users_mean ,Users_median
print DisUsers_records ,DisUsers_max ,DisUsers_min ,DisUsers_mean ,DisUsers_median 
# print PopUsers_records ,PopUsers_max ,PopUsers_min ,PopUsers_mean ,PopUsers_median 
# print RandUsers_records ,RandUsers_max ,RandUsers_min ,RandUsers_mean ,RandUsers_median



set key top left
set key samplen 1
set key font ",25"
set grid ytics xtics lt 0 lw 2 lc rgb "#B8B8B8"
set xlabel filename
set ylabel "CDF" offset 2,0
set yrange [0:1]
set format x "10^{%T}"
##################
set logscale  x 10

set xrange[0:*]

plot "Suitable/".filename using 1:(1./Users_records) smooth cumulative title "Suitable Users" lw 2 lt rgb "#76949F" ,\
"Disturbing/".filename using 1:(1./DisUsers_records) smooth cumulative title "Disturbing Users" lw 2 lt rgb '#981825' #, \
# "Popular/".filename using 1:(1./PopUsers_records) smooth cumulative title "Popular Users" lw 2 lt rgb '#0C7900' , \
# "Random/".filename using 1:(1./RandUsers_records) smooth cumulative title "Random Users" lw 2 lt rgb '#EBAF25'
