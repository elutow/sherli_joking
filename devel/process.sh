#!/bin/bash

set -eux

cd $(dirname $(dirname $(readlink -f $0)))
yapf -ipr sherlibot slowbro sherlibot_server.py tests
#mypy --ignore-missing-imports sherlibot slowbro sherlibot_server.py tests
pylint sherlibot sherlibot_server.py.py tests
