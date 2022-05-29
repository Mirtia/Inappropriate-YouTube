set terminal postscript enhanced eps color solid defaultplex \
    leveldefault  blacktext \
    dashlength 2.0 linewidth 3.0 butt \
    palfuncparam 2000,0.005 \
    "Helvetica" 30 


stats "../Data/Suitable/".filename using 1 nooutput name "Users"
stats "../Data/Disturbing/".filename using 1 nooutput name "DisUsers"

reset
set key at graph 0.24, 0.85 horizontal sample 0.1 

set size 2, 2 

set style data histogram
set style histogram cluster gap 0
set style fill solid border -1
set boxwidth 1

set xtics rotate by 90 scale 0 offset 0,-12
unset ytics
set y2tics rotate by 90
set grid y2tics lc rgb '#B8B8B8' lt 0 lw 4
set y2tics 0, 0.1 , 1 
set yrange [0:*]
set y2label "Percentage per User Category" font "Helvetica,280"
set xlabel "Categories" rotate by 180 offset 0,-15  font "Helvetica,280"

set title "Suitable and Disturbing Users categories (blue:Suitable, red:Disturbing)" font "Helvetica,280" offset 0,3 

set for [i=1:10] y2tics add (sprintf("%d%%%%",i*10) i/10.0)

set bmargin 20
set tmargin 10

set out "../Output/".filename.".eps"

plot "../Data/Suitable/".filename  using ($1/Users_sum) title "" lt rgb '#93BAF3', '' using 0:(0):xticlabel(2) ls 5 lw 10 w l title "", \
"../Data/Disturbing/".filename using ($1/DisUsers_sum) title "" lt rgb "#981825",  '' using 0:(0):xticlabel(2) w l title ""
