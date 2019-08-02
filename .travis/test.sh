
source $HOME/miniconda/bin/activate
export PATH="$HOME/miniconda/bin:$PATH"
conda activate swepy_env
python -m pytest -v --cov=swepy