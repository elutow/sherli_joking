#!/bin/bash

set -eux

cd $(dirname $(dirname $(readlink -f $0)))
yapf -ipr src tests
pylint src tests
