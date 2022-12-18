#!/bin/bash

PYTHON_EXE=/home/xuk9/anaconda3/envs/EmphysemaSeg/bin/python
SRC_ROOT=/home/xuk9/src/EmphysemaSeg

${PYTHON_EXE} ${SRC_ROOT}/EmphysemaSeg/main.py --config ${SRC_ROOT}/YAML/nlst_t2.YAML
