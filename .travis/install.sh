#!/bin/bash

if [$TRAVIS_OS_NAME = 'osx']; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    echo "conda activate base" >> ~/.bashrc
    source $HOME/miniconda/bin/activate
    conda config --set always_yes yes --set show_channel_urls true --set changeps1 no
    conda update -q conda
    conda config --add channels conda-forge
    conda info -a
    conda init bash
    conda env create -f test.yml
    conda activate swepy_env
    python setup.py install
    pip install dev_requirments.txt

else
    sudo apt-get update
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update conda
    conda info -a
    conda config --add channels conda-forge
    conda env create -f test.yml
    conda activate swepy_env
    python setup.py install
fi