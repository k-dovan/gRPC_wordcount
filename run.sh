#!/bin/bash

# clean previous output data
rm -rf intermediate
rm -rf out

python worker.py --name 1 &
python worker.py --name 2 &
python worker.py --name 3 &
python driver.py -N 6 -M 4 &