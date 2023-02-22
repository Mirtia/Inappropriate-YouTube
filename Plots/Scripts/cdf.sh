#!/bin/bash
dir=$1
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
	gnuplot -e "filename='$key'" ../GNUplot/plot_cdf.plt
done
gnuplot -e "filename='madeForKids'" ../GNUplot/madeForKids_box.plt
gnuplot ../GNUplot/meaningcloud.plt
gnuplot -e "filename='keywords'" ../GNUplot/sentiStrength.plt
gnuplot -e "filename='description'" ../GNUplot/sentiStrength.plt
# Plots ECDF of each key
