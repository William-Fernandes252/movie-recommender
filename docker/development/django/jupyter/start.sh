
#!/bin/bash

set -o errexit
set -o nounset


cd /app/src
jupyter notebook --allow-root --ip=0.0.0.0
