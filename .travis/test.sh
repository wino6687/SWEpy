if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
  source activate venv
  python -m pytest -v
else
  source $HOME/miniconda/bin/activate
  export PATH="$HOME/miniconda/bin:$PATH"
  python -m pytest -v
fi