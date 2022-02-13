#!/bin/bash
dir=$(pwd)
echo $dir
if [ -z $dir ]; then
	echo "'dir' variable is not set."
fi

keys=(
	"descriptionCharCount"
	"keywordsCount"
	"subscriberCount"
	"topicCount"
	"videoCount" 
	"viewCount"	
	"subscriptionCount"
	"postCount"	
)

for key in ${keys[*]};
do	
	echo $key
	gnuplot -e "filename='$key'" plot_cdf.plt
done
gnuplot -e "filename='madeForKids'" madeForKids_box.plt 
gnuplot meaningcloud.plt
gnuplot -e "filename='keywords'" sentiStrength.plt
gnuplot -e "filename='description'" sentiStrength.plt
# Plots ECDF of each key