#!/bin/bash

PYTHON_EXE=/home/local/VANDERBILT/xuk9/anaconda3/envs/EmphysemaSeg/bin/python
SRC_ROOT=/nfs/masi/xuk9/src/EmphysemaSeg

${PYTHON_EXE} ${SRC_ROOT}/EmphysemaSeg/main.py --config ${SRC_ROOT}/YAML/nlst_experimental.YAML
