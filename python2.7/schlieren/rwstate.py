import multiprocessing as mp
import os


class RWStateMachine(object):

    def __init__(self, nwrite=1, nread=1, start_write=True, name=None):
        self.monitor = mp.Lock()
        self.write_state = mp.Value('b', start_write)
        self.read_pids = mp.Array('i', [0 for _i in xrange(nread)])
        self.write_pids = mp.Array('i', [0 for _i in xrange(nwrite)])
        self.read_signal = mp.Condition(self.monitor)
        self.write_signal = mp.Condition(self.monitor)
        self.name = name

    def acquire_read(self, pid=None):
        if pid is None:
            pid = os.getpid()
        self.monitor.acquire()
        while self.write_state.value or pid in self.read_pids:
            self.read_signal.wait()
        self.set_read_pid(pid)
        self.monitor.release()

    def set_read_pid(self, pid):
        with self.read_pids.get_lock():
            assert pid not in self.read_pids, '{} {}'.format(
                pid, [x for x in self.read_pids])
            assert 0 in self.read_pids, '{} {}'.format(
                pid, [x for x in self.read_pids])
            for i in xrange(len(self.read_pids)):
                if self.read_pids[i] == 0:
                    self.read_pids[i] = pid
                    break

    def acquire_write(self, pid=None):
        if pid is None:
            pid = os.getpid()
        self.monitor.acquire()
        while not self.write_state.value or pid in self.write_pids:
            self.write_signal.wait()
        self.set_write_pid(pid)
        self.monitor.release()

    def set_write_pid(self, pid):
        with self.write_pids.get_lock():
            assert pid not in self.write_pids, '{} {}'.format(
                pid, [x for x in self.write_pids])
            assert 0 in self.write_pids, '{} {}'.format(
                pid, [x for x in self.write_pids])
            for i in xrange(len(self.write_pids)):
                if self.write_pids[i] == 0:
                    self.write_pids[i] = pid
                    break

    def release(self):
        self.monitor.acquire()
        if self.write_state.value and 0 not in self.write_pids:
            with self.write_pids.get_lock():
                self.write_pids[:] = [0 for _i in xrange(len(self.write_pids))]
                self.write_state.value = False
        elif not self.write_state.value and 0 not in self.read_pids:
            with self.read_pids.get_lock():
                self.read_pids[:] = [0 for _i in xrange(len(self.read_pids))]
                self.write_state.value = True
        self.monitor.release()
        if self.write_state.value:
            self.write_signal.acquire()
            self.write_signal.notify()
            self.write_signal.release()
        else:
            self.read_signal.acquire()
            self.read_signal.notify()
            self.read_signal.release()


class RWStateLockedData(RWStateMachine):

    def __init__(self, data, *args, **dargs):
        super(RWStateLockedData, self).__init__(*args, **dargs)
        self.data = data

    def get_data(self):
        return self.data

import time


def test():

    def writer(_state_machine):
        pid = os.getpid()
        _state_machine.acquire_write(pid=pid)
        _state_machine.release()

    def reader(_state_machine):
        pid = os.getpid()
        _state_machine.acquire_read(pid=pid)
        _state_machine.release()

    state_machine = RWStateMachine()

    r1 = mp.Process(target=reader, args=(state_machine,))
    r1.start()

    r2 = mp.Process(target=reader, args=(state_machine,))
    r2.start()

    w1 = mp.Process(target=writer, args=(state_machine,))
    w1.start()

    w2 = mp.Process(target=writer, args=(state_machine,))
    w2.start()

    w1.join()
    w2.join()
    r1.join()
    r2.join()


def test_more():

    N = 5000

    def src(out_machine):
        pid = os.getpid()
        for _i in xrange(N):
            out_machine.acquire_write(pid=pid)
            out_machine.release()

    def node(src_machine, dst_machine):
        pid = os.getpid()
        for _i in xrange(N):
            src_machine.acquire_read(pid=pid)
            dst_machine.acquire_write(pid=pid)
            dst_machine.release()
            src_machine.release()

    def snk(dst_machine):
        pid = os.getpid()
        for _i in xrange(N):
            dst_machine.acquire_read(pid=pid)
            dst_machine.release()

    m1 = RWStateMachine(nread=2, name='m1')
    m2 = RWStateMachine(name='m2', nread=2)
    m3 = RWStateMachine(name='m3')

    src1 = mp.Process(target=src, args=(m1,))
    node1 = mp.Process(target=node, args=(m1, m2))
    node2 = mp.Process(target=node, args=(m2, m3))
    snk1 = mp.Process(target=snk, args=(m2,))
    snk2 = mp.Process(target=snk, args=(m1,))
    snk3 = mp.Process(target=snk, args=(m3,))

    src1.start()
    node1.start()
    node2.start()
    snk1.start()
    snk2.start()
    snk3.start()

    src1.join()
    node1.join()
    node2.join()
    snk1.join()
    snk2.join()
    snk3.join()
