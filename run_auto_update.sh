#!/bin/bash

run_dir="/tmp/auto-update"

# clean up and recreate temp directory
if [ -d "$run_dir" ]; then
	rm -r "$run_dir"
fi
mkdir -p "$run_dir"

# copy python file and environment to temp directory
cp "auto-update.py" "$run_dir/"
cp -r "env" "$run_dir/"

# run the python script
$run_dir/env/bin/python $run_dir/auto-update.py -quiet

# clean up temp directory
if [ -d "$run_dir" ]; then
	rm -r "$run_dir"
fi
