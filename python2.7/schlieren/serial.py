import logging
LOG = logging.getLogger(__name__)

import numpy as np

from .rwstate import RWStateLockedData
from .lib import *


class SchlierenPipeline(object):

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def run(self):
        first_peaks = None
        first_centroids = None
        while True:
            frame = self.src.next()
            if frame is None:
                break
            gray_frame = grayscale_image(frame)
            if first_peaks is None:
                first_peaks = find_peaks(gray_frame)
            total = convolve(gray_frame, TOTAL_KERNEL)
            rgrad = convolve(gray_frame, ROW_KERNEL)
            cgrad = convolve(gray_frame, COL_KERNEL)
            rcent = divide(rgrad, total)
            ccent = divide(cgrad, total)
            if first_centroids is None:
                first_centroids = rcent, ccent
            rcent0, ccent0 = first_centroids
            rdiff = subtract(rcent, rcent0)
            cdiff = subtract(ccent, ccent0)
            rpeaks = apply_peaks(rdiff, first_peaks)
            cpeaks = apply_peaks(cdiff, first_peaks)
            rcond = condense(rpeaks)
            ccond = condense(cpeaks)
            rcmap = apply_cmap(rcond)
            ccmap = apply_cmap(ccond)
            output = join(rcmap, ccmap)
            self.dst.write(output)


def test_and_set(test, src, out=None, fn=None):
    if test.get():
        return
    result = True
    if fn is None:
        out[:] = src
    else:
        result = fn(src, out=out)
    test.set(result is not None)


class SharedValue(object):

    def __init__(self, init_val):
        self.val = init_val

    def set(self, new_val):
        self.val = new_val

    def get(self):
        return self.val


class PreallocSchlierenPipeline(object):

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

        self.peaks_test = SharedValue(False)
        self.rcent0_test = SharedValue(False)
        self.ccent0_test = SharedValue(False)

        frame_shape = self.src.get_frame_shape()
        self.frame = np.zeros(frame_shape, dtype='uint8')
        self.gray_frame = np.zeros(frame_shape[:2], dtype=float)
        self.total = np.zeros(frame_shape[:2], dtype=float)
        self.peaks = np.zeros(frame_shape[:2], dtype=bool)
        self.rgrad = np.zeros(frame_shape[:2], dtype=float)
        self.cgrad = np.zeros(frame_shape[:2], dtype=float)
        self.rcent = np.zeros(frame_shape[:2], dtype=float)
        self.ccent = np.zeros(frame_shape[:2], dtype=float)
        self.rcent0 = np.zeros(frame_shape[:2], dtype=float)
        self.ccent0 = np.zeros(frame_shape[:2], dtype=float)
        self.rdiff = np.zeros(frame_shape[:2], dtype=float)
        self.cdiff = np.zeros(frame_shape[:2], dtype=float)
        self.rpeaks = np.zeros(frame_shape[:2], dtype=float)
        self.cpeaks = np.zeros(frame_shape[:2], dtype=float)
        self.rcond = np.zeros(frame_shape[:2], dtype=float)
        self.ccond = np.zeros(frame_shape[:2], dtype=float)
        self.rcmap = np.zeros(frame_shape[:2] + (4,), dtype='uint8')
        self.ccmap = np.zeros(frame_shape[:2] + (4,), dtype='uint8')
        self.output = np.zeros((frame_shape[0], 2 * frame_shape[1], 4), dtype='uint8')
        self.output2 = np.zeros((frame_shape[0], 2* frame_shape[1]), dtype=float)

    def run(self):
        while True:
            self.frame = self.src.next()
            if self.frame is None:
                break
            grayscale_image(self.frame, out=self.gray_frame)
            test_and_set(self.peaks_test, self.gray_frame, self.peaks, fn=find_peaks)
            convolve(self.gray_frame, TOTAL_KERNEL, out=self.total)
            convolve(self.gray_frame, ROW_KERNEL, out=self.rgrad)
            convolve(self.gray_frame, COL_KERNEL, out=self.cgrad)
            divide(self.rgrad, self.total, out=self.rcent)
            divide(self.cgrad, self.total, out=self.ccent)
            test_and_set(self.rcent0_test, self.rcent, self.rcent0)
            test_and_set(self.ccent0_test, self.ccent, self.ccent0)
            subtract(self.rcent, self.rcent0, out=self.rdiff)
            subtract(self.ccent, self.ccent0, out=self.cdiff)
            apply_peaks(self.rdiff, self.peaks, out=self.rpeaks)
            apply_peaks(self.cdiff, self.peaks, out=self.cpeaks)
            condense(self.rpeaks, out=self.rcond)
            condense(self.cpeaks, out=self.ccond)
            apply_cmap(self.rcond, out=self.rcmap)
            apply_cmap(self.ccond, out=self.ccmap)
            join(self.rcmap, self.ccmap, out=self.output)
            self.dst.write(self.output)

            # Inelegant way of getting data so I can deal with it somewhere else
            # I should apply the cmap here but currently don't
            #join2(self.rcond,self.ccond,out=self.output2)
            #self.dst.write(self.output2)

DefaultPipeline = PreallocSchlierenPipeline
