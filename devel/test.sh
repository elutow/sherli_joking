#!/bin/bash

set -eux

cd $(dirname $(dirname $(readlink -f $0)))
pytest
