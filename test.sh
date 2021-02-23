#!/bin/bash
x=1; while [ $x -le 1000000 ]; do echo "$x" $(( x++ )); done
