import numpy as np
import scipy.ndimage as nd
import matplotlib.cm as cm
import matplotlib as plt
import cv2

TOTAL_KERNEL = np.array([(1, 1, 1), (1, 1, 1), (1, 1, 1)], dtype=float)
ROW_KERNEL = np.array([(-1, -1, -1), (0, 0, 0), (1, 1, 1)], dtype=float)
COL_KERNEL = np.array([(-1, 0, 1), (-1, 0, 1), (-1, 0, 1)], dtype=float)


def grayscale_image(image, out=None):
    result = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(float, copy=False)
    if out is None:
        return result
    out[:] = result
    return out


def find_peaks(image, thresh=20, size=(3, 3), out=None):
    result = (image == nd.maximum_filter(image, size=size)) & (image >= thresh)
    if out is None:
        return result
    out[:] = result
    return out


def divide(x, y, out=None):
    if out is None:
        return np.divide(x, y)
    return np.divide(x, y, out=out)


def apply_peaks(image, mask, out=None):
    if out is None:
        image_copy = np.copy(image)
        image_copy[~mask] = 0
        return image_copy
    else:
        out[:] = image
        out[~mask] = 0
        return out


def condense(image, size=(10, 10), out=None):
    return nd.maximum_filter(image, size=size, output=out)


def convolve(image, kernel, out=None):
    return nd.convolve(image.astype(float), kernel, output=out)


def subtract(x, y, out=None):
    if out is None:
        return np.subtract(x, y)
    return np.subtract(x, y, out=out)


def apply_cmap(image, cmap=cm.bone, out=None, vmin=-.3, vmax=.3):
    cmap = cm.ScalarMappable(norm=plt.colors.Normalize(vmin, vmax), cmap=cmap)
    result = cmap.to_rgba(image, bytes=True)
    if out is None:
        return result
    out[:] = result
    return out

def join2(image1, image2, out=None):
    # Part of a inelegant hack
    if out is None:
        return np.hstack([image1, image2])
    else:
        out[:, :image1.shape[1]] = image1
        out[:, image2.shape[1]:] = image2
        return out

def join(image1, image2, out=None):
    if out is None:
        return np.hstack([image1, image2])
    else:
        out[:, :image1.shape[1], :] = image1
        out[:, image2.shape[1]:, :] = image2
        return out
