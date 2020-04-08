#!/bin/bash
set -e
./compile.sh
python run_mvk_server.py $1
