#!/bin/bash
source ./venv/bin/activate
pip install -r requirements.txt
python index_srsi.py $*

