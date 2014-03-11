import logging
LOG = logging.getLogger(__name__)

import os
import time

import multiprocessing as mp
import npshm as shm

from .lib import *
from .rwstate import RWStateLockedData as DataLock


def locked_test_and_set(test, src, out=None, fn=None):
    with test.get_lock():
        if test.value:
            return
        if fn is None:
            out[:] = src
        else:
            fn(src, out=out)
        test.value = True


class SharedmemSchlierenPipeline(object):

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

        self.peaks_test = mp.Value('b', False)
        self.rcent0_test = mp.Value('b', False)
        self.ccent0_test = mp.Value('b', False)

        frame_shape = self.src.get_frame_shape()
        self.frame = DataLock(
            shm.zeros(frame_shape, dtype='uint8'),
            name='frame')
        self.gray_frame = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                                   name='gray_frame',
                                   nread=4)
        self.total = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='total',
                              nread=2)
        self.peaks = DataLock(shm.zeros(frame_shape[:2], dtype=bool),
                              name='peaks',
                              nread=2)
        self.rgrad = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='rgrad')
        self.cgrad = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='cgrad')
        self.rcent = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='rcent',
                              nread=2)
        self.ccent = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='ccent',
                              nread=2)
        self.rcent0 = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                               name='rcent0')
        self.ccent0 = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                               name='ccent0')
        self.rdiff = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='rdiff')
        self.cdiff = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='cdiff')
        self.rpeaks = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                               name='rpeaks')
        self.cpeaks = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                               name='cpeaks')
        self.rcond = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='rcond')
        self.ccond = DataLock(shm.zeros(frame_shape[:2], dtype=float),
                              name='ccond')
        self.rcmap = DataLock(shm.zeros(frame_shape[:2] + (4,), dtype='uint8'),
                              name='rcmap')
        self.ccmap = DataLock(shm.zeros(frame_shape[:2] + (4,), dtype='uint8'),
                              name='ccmap')
        self.output = DataLock(shm.zeros((frame_shape[0], 2 * frame_shape[1], 4), dtype='uint8'),
                               name='output')

        self.running = mp.Value('b', True)
        self.procs = []

    def run(self):
        self.make_controller(self.src.next,
                             out=self.frame)  # 72 fps
        self.make_worker(grayscale_image,
                         self.frame,
                         out=self.gray_frame)  # 130 fps
        self.make_worker(locked_test_and_set,
                         self.peaks_test,
                         self.gray_frame,
                         out=self.peaks,
                         fn=find_peaks)  # 4.5k fps
        self.make_worker(convolve,
                         self.gray_frame,
                         TOTAL_KERNEL,
                         out=self.total)  # 40 fps
        self.make_worker(convolve,
                         self.gray_frame,
                         ROW_KERNEL,
                         out=self.rgrad)  # 52 fps
        self.make_worker(convolve,
                         self.gray_frame,
                         COL_KERNEL,
                         out=self.cgrad)  # 46 fps
        self.make_worker(divide,
                         self.rgrad,
                         self.total,
                         out=self.rcent)  # 152 fps
        self.make_worker(divide,
                         self.cgrad,
                         self.total,
                         out=self.ccent)  # 144 fps
        self.make_worker(locked_test_and_set,
                         self.rcent0_test,
                         self.rcent,
                         out=self.rcent0)  # 36k fps
        self.make_worker(locked_test_and_set,
                         self.ccent0_test,
                         self.ccent,
                         out=self.ccent0)  # 36k fps
        self.make_worker(subtract,
                         self.rcent,
                         self.rcent0,
                         out=self.rdiff)  # 258 fps
        self.make_worker(subtract,
                         self.ccent,
                         self.ccent0,
                         out=self.cdiff)  # 258 fps
        self.make_worker(apply_peaks,
                         self.rdiff,
                         self.peaks,
                         out=self.rpeaks)  # 144 fps
        self.make_worker(apply_peaks,
                         self.cdiff,
                         self.peaks,
                         out=self.cpeaks)  # 144 fps
        self.make_worker(condense,
                         self.rpeaks,
                         out=self.rcond)  # 22 fps
        self.make_worker(condense,
                         self.cpeaks,
                         out=self.ccond)  # 22 fps
        self.make_worker(apply_cmap,
                         self.rcond,
                         out=self.rcmap)  # 35 fps
        self.make_worker(apply_cmap,
                         self.ccond,
                         out=self.ccmap)  # 35 fps
        self.make_worker(join,
                         self.rcmap,
                         self.ccmap,
                         out=self.output)  # 296 fps
        self.make_worker(self.dst.write, self.output)  # 26k fps
        self.join_all()

    def worker_loop(self, _func, *args, **dargs):
        new_args = tuple(
            [a.get_data() if isinstance(a, DataLock) else a for a in args])
        new_dargs = dict(
            [(k, v.get_data()) if isinstance(v, DataLock) else (k, v) for k, v in dargs.items()])
        read_locks = [a for a in args if isinstance(a, DataLock)]
        write_locks = [d for d in dargs.values() if isinstance(d, DataLock)]
        while True:
            with self.running.get_lock():
                if not self.running.value:
                    break
            [l.acquire_read() for l in read_locks]
            [l.acquire_write() for l in write_locks]
            _func(*new_args, **new_dargs)
            [l.release() for l in write_locks]
            [l.release() for l in read_locks]

    def controller_loop(self, _func, *args, **dargs):
        new_args = tuple(
            [a.get_data() if isinstance(a, DataLock) else a for a in args])
        new_dargs = dict(
            [(k, v.get_data()) if isinstance(v, DataLock) else (k, v) for k, v in dargs.items()])
        read_locks = [a for a in args if isinstance(a, DataLock)]
        write_locks = [d for d in dargs.values() if isinstance(d, DataLock)]
        while True:
            [l.acquire_read() for l in read_locks]
            [l.acquire_write() for l in write_locks]
            result = _func(*new_args, **new_dargs)
            [l.release() for l in write_locks]
            [l.release() for l in read_locks]
            if result is None:
                with self.running.get_lock():
                    self.running.value = False
                break

    def make_worker(self, _func, *args, **kwargs):
        proc = mp.Process(target=self.worker_loop, 
                          args=(_func,) + args, 
                          kwargs=kwargs)
        proc.start()
        self.procs.append(proc)

    def make_controller(self, _func, *args, **kwargs):
        proc = mp.Process(target=self.controller_loop,
                          args=(_func,) + args,
                          kwargs=kwargs)
        proc.start()
        self.procs.append(proc)

    def join_all(self):
        [p.join() for p in self.procs]

DefaultPipeline = SharedmemSchlierenPipeline
