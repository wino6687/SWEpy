import numpy as np
import swepy.classify as classify
import pytest
import matplotlib
import os


@pytest.fixture
def swe():
    print(os.listdir())
    swe = np.load("swepy/tests/swe_testfile.npy")
    return swe


def test_govf():
    """
    Ensure proper result from savgol filter
    """
    np.random.seed(1)
    array = np.random.rand(1, 10, 10)
    res = classify.govf(array.ravel(), 4)
    assert res == 0.9476204544544236


def test_optimal_jenk(swe):
    """
    Ensure the correct number of classes is returned by optimal jenk
    on test image that has been verified.
    """
    n_classes = classify.optimal_jenk(swe.ravel(), 0.8)
    assert n_classes[0] == 4


def test_optimal_jenk_bounds(swe):
    """
    Ensure the correct class bounds are found for test swe image
    """
    info = classify.optimal_jenk(swe.ravel(), 0.8)
    assert info[1] == [
        22.024993896484375,
        27.162506103515625,
        30.257492065429688,
        33.41499328613281,
        38.93499755859375,
    ]


def test_plot_jenk(swe):
    """
    Ensure no erros and proper figure generated
    when plotting jenks on an image
    """
    fig = classify.plot_jenks(swe, 0.8, True)
    assert type(fig) == matplotlib.figure.Figure
