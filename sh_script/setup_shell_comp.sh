#!/bin/bash

# retrieve abs path of this script and this to the PYTHONPATH env var
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR
echo "Added $SCRIPT_DIR to PYTHONPATH"

# install HYDRA SHELL COMPLETIONS FOR current type of shell (bash OR fish OR zsh)
# NOTE: this is only for the current shell session

for python_file in 'Milestone2/training_main.py' 'Milestone2/hp_opt_main.py'; do
    shell_type=$(basename "$SHELL")
    echo "Installing $shell_type HYDRA completions for $python_file"
    eval "$(python "$SCRIPT_DIR"/$python_file -sc install="$shell_type")"
done