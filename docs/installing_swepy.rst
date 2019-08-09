Installing SWEpy:
=================

SWEpy is published and maintained on both ``pip`` and ``conda-forge``.

You can create a conda environemnt using the provided yml file, ``swepy_env.yml`` to get up and running right away. 

In your terminal, navigate to the directory containing your yml file and run the following command:

``conda env create -f swepy_env.yml``

``source activate swepy_env``

or 

``conda activate swepy_env``

Importing SWEpy in Python
-------------------------

Now in Python you will be able to import SWEpy and its submodules. 

    >>> import swepy
    >>> import swepy.pipeline as pipe
    >>> import swepy.process as sp
    >>> import swepy.analysis as sa
    >>> import swepy.nsidcDownloader as sd

