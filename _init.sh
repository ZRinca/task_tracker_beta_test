#!/bin/bash

cd "$(dirname "$0")"
pip3 install virtualenv
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
exec $SHELL