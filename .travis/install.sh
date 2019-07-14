#!/bin/bash

if [$TRAVIS_OS_NAME = 'osx']; then
    brew update
    # Per the `pyenv homebrew recommendations <https://github.com/yyuu/pyenv/wiki#suggested-build-environment>`_.
    brew install openssl readline
    # See https://docs.travis-ci.com/user/osx-ci-environment/#A-note-on-upgrading-packages.
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    pyenv install $PYTHON
    export PYENV_VERSION=$PYTHON
    export PATH="/Users/travis/.pyenv/shims:${PATH}"
    pyenv-virtualenv venv
    source venv/bin/activate
    brew install gdal --HEAD
    pip install -r requirements.txt
    python setup.py install

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
    source activate swepy_env
    python setup.py install
fi