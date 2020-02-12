import numpy as np
from numpy.lib.stride_tricks import as_strided


def view_blocks(array, block_shape):
    """
    View SWE image in non-overlapping blocks (numpy re-striding)

    Based off of the scikit-image view_as_blocks function
    """
    if not isinstance(block_shape, tuple):
        raise TypeError("block must be a tuple")

    block_shape = np.array(block_shape)
    if (block_shape <= 0).any():
        raise ValueError("'block_shape' elements must be positive")

    if block_shape.size != array.ndim:
        raise ValueError(
            "'block_shape' must have the same length " "as 'array.shape'"
        )
    array_shape = np.array(array.shape)
    if (array_shape % block_shape).sum() != 0:
        raise ValueError("'block_shape' is not compatible with 'array'")

    new_shape = tuple(array_shape // block_shape) + tuple(block_shape)
    new_strides = tuple(array.strides * block_shape) + array.strides
    array_final = as_strided(array, shape=new_shape, strides=new_strides)
    return array_final


def downsample(im, block_size, func=np.sum, padval=0, f_kwargs=None):
    """
    Downsample given SWE image using a specific numpy function

    Function is applied to blocks locally

    Inspired by sci-kit image's ``block_reduce`` function

    Parameters
    ----------
    im: np.array
        N-dim image
    block_size: np.array
        array with downsampling integer factor for each axis
    func: any callable function (numpy ideal)
        Function to calculate values on every block. Should
        accept an axis. Examples funcs are ``np.sum``, ``np.min``,
        ``np.mean``, etc.
    padval: float
        Constant pad value if im not divisible by block size
    f_kwargs: dict
        Keyword args passed to ``func``.
        e.g. ``f_kwargs={'dtype':np.float16}`` to pass dtype to ``np.mean``
    """

    if len(block_size) != im.ndim:
        raise ValueError(
            "`block_size` must have the same length " "as 'im.shape`."
        )
    if f_kwargs is None:
        f_kwargs = {}

    pad_width = []
    for i in range(len(block_size)):
        if block_size[i] < 1:
            raise ValueError("Down-sampling factors must be >= 1")
        if im.shape[i] % block_size[i] != 0:
            after_width = block_size[i] - (im.shape[i] % block_size[i])
        else:
            after_width = 0
        pad_width.append((0, after_width))

    im = np.pad(
        im, pad_width=pad_width, mode="constant", constant_values=padval
    )
    block = view_blocks(im, block_size)

    return func(block, axis=tuple(range(im.ndim, block.ndim)), **f_kwargs)
