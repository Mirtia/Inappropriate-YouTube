#!/bin/bash
dir=$(pwd)
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

shopt -s extglob
for subdir in ${subdirs[*]}; 
do
	for file in $dir/$subdir/!(*Count|*.plt|*.sh|*.py);
	do
			echo $file
			sort $file| uniq -c | sort -k 2 -o $file
	done
done


# Sort alphanumeric columns