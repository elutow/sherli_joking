#!/bin/bash

set -eux

cd $(dirname $(dirname $(readlink -f $0)))
yapf -ipr sherlibot slowbro sherli_server.py tests
pylint sherlibot slowbro sherli_server.py tests
