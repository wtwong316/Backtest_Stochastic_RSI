#!/bin/bash
source ./venv/bin/activate
pip install -r requirements.txt
python backtest_srsi.py $*

