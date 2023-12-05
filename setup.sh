#!/bin/bash

cd $(dirname $0)
python -m pip install --upgrade pip
python -m pip install poetry
python -m poetry install --no-root
