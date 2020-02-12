import numpy as np
import swepy.classify as classify


def test_govf():
    """
    Ensure proper result from savgol filter
    """
    np.random.seed(1)
    array = np.random.rand(1, 10, 10)
    res = classify.govf(array.ravel(), 4)
    assert res == 0.9476204544544236
