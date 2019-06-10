#!/bin/bash

set -eux

cd $(dirname $(dirname $(readlink -f $0)))
yapf -ipr sherlibot nemo_utils slowbro sherlibot_server.py tests
#mypy --ignore-missing-imports sherlibot slowbro sherlibot_server.py tests
pylint sherlibot slowbro sherlibot_server.py tests
