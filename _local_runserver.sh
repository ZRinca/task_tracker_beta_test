#!/bin/bash
cd "$(dirname "$0")"

source env/bin/activate

python3 manage.py runserver


