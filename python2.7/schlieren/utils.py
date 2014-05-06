import cv2
import os
import scipy.misc
from glob import iglob
import matplotlib.pyplot as plt
import time


def src_from_path(path):
    if isinstance(path, int):
        return CameraSrc(path)
    path = os.path.abspath(path)
    if os.path.isdir(path):
        return DirectorySrc(path)
    elif os.path.isfile(path):
        return VideoFileSrc(path)
    else:
        return CameraSrc(path)


class FrameSrc(object):

    def __init__(self, path):
        raise NotImplementedError()

    def next(self):
        raise NotImplementedError()

    def __iter__(self):
        while True:
            result = self.next()
            if result is None:
                break
            yield result

    def get_frame_shape(self):
        raise NotImplementedError()


class CvFrameSrc(FrameSrc):

    def __init__(self, token):
        self.cap = cv2.VideoCapture(token)
        assert self.cap.isOpened(), "Failed to open {}".format(token)

    def next(self):
        success, frame = self.cap.read()
        return frame

    def get_frame_shape(self):
        return tuple([self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT),
                      self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH),
                      8#self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_DEPTH),
                      ])


class DirectorySrc(FrameSrc):

    def __init__(self, path, glob=None):
        if glob is None:
            glob = '*.*'
        self.files = sorted(iglob(os.path.join(path, glob)))

    def get_frame_shape(self):
        return scipy.misc.imread(self.files[0]).shape

    def next(self, out=None):
        try:
            next_file = self.files.pop(0)
        except IndexError, e:
            return None
        frame = scipy.misc.imread(next_file)
        if out is None:
            return frame
        out[:] = frame
        return out


class CameraSrc(CvFrameSrc):

    def __init__(self, token):
        device_number = token
        if isinstance(token, str):
            # this is buggy if you have >9 cameras
            device_number = int(token[-1])
        super(CameraSrc, self).__init__(device_number)


class VideoFileSrc(CvFrameSrc):

    def __init__(self, path):
        super(VideoFileSrc, self).__init__(path)


def snk_from_path(path):
    root, ext = os.path.splitext(path)
    if ext == '.h5':
        return H5Snk(path)
    elif ext in ['.avi', ]:
        return VideoFileSnk(path)


class FrameSnk(object):

    def write(self, frame):
        raise NotImplementedError()


class CvFrameSnk(FrameSnk):

    def __init__(self, token):
        raise NotImplementedError()


class CounterSnk(FrameSnk):

    def __init__(self, *args, **dargs):
        self.count = 0
        self.t0 = None
        super(FrameSnk, self).__init__(*args, **dargs)

    def write(self, frame):
        if self.t0 is None:
            self.t0 = time.time() - .1
        if frame is None:
            return
        self.count += 1
        fps = float(self.count) / (time.time() - self.t0)
        print "{} @ {:.2f} fps".format(self.count, fps)
