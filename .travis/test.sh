if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
  source $HOME/miniconda/bin/activate
  export PATH="$HOME/miniconda/bin:$PATH"
  conda activate earthpy-dev
  python -m pytest -v
else
  python -m pytest -v
fi