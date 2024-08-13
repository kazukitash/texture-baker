#!/bin/bash

script_dir=$(cd $(dirname $0) && pwd)

blender -b $1 -y -P $script_dir/cli.py
