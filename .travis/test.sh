if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
  source $HOME/miniconda/bin/activate
  export PATH="$HOME/miniconda/bin:$PATH"
  source activate swepy_env
  python -m pytest -v
else
  source $HOME/miniconda/bin/activate
  export PATH="$HOME/miniconda/bin:$PATH"
  conda activate swepy_env
  python -m pytest -v
fi