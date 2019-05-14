#!/bin/bash

set -eux

# For pip-compile
export CUSTOM_COMPILE_COMMAND="./devel/update_requirements.sh"

pip-compile -U devel/dev-requirements.in
pip-compile -U requirements.in
pip install -Ur devel/dev-requirements.txt
pip install -Ur requirements.txt
