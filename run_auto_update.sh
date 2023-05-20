#!/bin/bash

run_dir="/tmp/auto-update"
script_dir="$(realpath $(dirname $0))"

# clean up and recreate temp directory
if [ -d "$run_dir" ]; then
	rm -r "$run_dir"
fi
mkdir -p "$run_dir"

# copy python file and environment to temp directory
cp "$script_dir/auto-update.py" "$run_dir/"
cp -r "$script_dir/env" "$run_dir/"

# run the python script
$run_dir/env/bin/python $run_dir/auto-update.py "$script_dir"
