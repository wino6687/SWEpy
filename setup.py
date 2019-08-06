import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swepy",
    version="1.5.2",
    author="William Norris",
    author_email="wino6687@colorado.edu",
    description="A python package for obtaining and manipulating Tb files from the MEaSUREs database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wino6687/SWEpy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ),
)
