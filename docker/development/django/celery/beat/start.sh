#!/bin/bash

set -o errexit
set -o nounset


rm -f './celerybeat.pid'
cd /app/src
exec watchfiles --filter python celery.__main__.main --args '-A config beat -l INFO'
