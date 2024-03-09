#!/bin/bash

set -o errexit
set -o nounset

cd /app/src
exec watchfiles --filter python celery.__main__.main --args '-A config worker -l INFO'
