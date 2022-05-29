#!/bin/bash
dir=$1
echo $dir
if [ -z $dir ]; then
	echo "'dir' variable is not set."
fi

subdirs=(
	"Suitable" 
	"Disturbing"
	"Popular"
	"Random"
)

for subdir in ${subdirs[*]}; 
do

	for file in $dir/$subdir/*"Count";
	do
			echo $file
			sort -n -o $file $file
	done
done