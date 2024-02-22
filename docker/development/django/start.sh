#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python src/manage.py migrate
python src/manage.py runserver 0.0.0.0:8000
