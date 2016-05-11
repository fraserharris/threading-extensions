from multiprocessing import Value
from nose.tools import assert_equals, assert_greater
from time import sleep
import unittest

from threading_extensions import StoppableThread, ExceptionThread, StoppableExceptionThread


class StoppableThreadTests(unittest.TestCase):
    def target_finishes_test(self):
        """ run target function """
        def target_finite(stop_event):
            while not stop_event.is_set():
                stop_event.wait(1)
                return

        st = StoppableThread(target=target_finite)
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.join()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), False)

    def target_with_args_finishes_test(self):
        """ run target function loop 5 times """

        def target_finite(x, stop_event):
            stop_event.wait(0.5)
            while not stop_event.is_set():
                with x.get_lock():
                    x.value += 1
                    if x.value > 5:
                        break

        x = Value('i', 0)
        st = StoppableThread(target=target_finite, args=(x,))
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.join()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_equals(x.value, 6)

    def target_stop_test(self):
        """ stop infinite-loop target function """
        def target_infinite(stop_event):
            while not stop_event.is_set():
                stop_event.wait(1)

        st = StoppableThread(target=target_infinite)
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.stop()
        assert_equals(st.stopped, True)
        st.join()
        assert_equals(st.is_alive(), False)

    def run_finishes_test(self):
        """ Subclass StoppableThread and finish method `run` """
        class WaitThread(StoppableThread):
            def run(self):
                self._stop.wait(0.5)
                while not self._stop.is_set():
                    return

        wt = WaitThread()
        wt.start()
        assert_equals(wt.stopped, False)
        assert_equals(wt.is_alive(), True)
        wt.join()
        assert_equals(wt.stopped, False)
        assert_equals(wt.is_alive(), False)

    def run_stop_test(self):
        """ Subclass StoppableThread and stop method `run` """
        class IncrementThread(StoppableThread):
            """ Used to test _stop in `run` """
            def __init__(self, *args, **kwargs):
                self.x = args[0]
                super(IncrementThread, self).__init__(*args[1:], **kwargs)

            def run(self):
                while not self._stop.is_set():
                    with self.x.get_lock():
                        self.x.value += 1

        x = Value('i', 0)
        st = IncrementThread(x)
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        sleep(0.5)
        st.stop()
        assert_equals(st.stopped, True)
        st.join()
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_greater(x.value, 0)


class ExceptionTheadTests(unittest.TestCase):
    """ Subclass ExceptionThread """
    class PassThread(ExceptionThread):
        def run_with_exception(self):
            pass

    class RaiseThread(ExceptionThread):
        def run_with_exception(self):
            raise ValueError('eep!')

    def no_exceptions_test(self):
        pt = self.PassThread()
        pt.start()
        pt.join()
        assert_equals(pt.is_alive(), False)

    def exceptions_test(self):
        rt = self.RaiseThread()
        rt.start()
        # Depending on thread timing, this rt.is_alive() is sometimes True or False
        # at this point. Each value is a different code path, and this test is meant
        # to demonstrate the True codepath.
        # assert_equals(rt.is_alive(), True)
        with self.assertRaises(ValueError):
            rt.join()

    def exception_retrieved_later_test(self):
        rt = self.RaiseThread()
        rt.start()
        sleep(1)
        assert_equals(rt.is_alive(), False)
        with self.assertRaises(ValueError):
            rt.join()

    def join_twice_test(self):
        """ join must know that thread is already dead and not hang """
        pt = self.PassThread()
        pt.start()
        pt.join()
        assert_equals(pt.is_alive(), False)
        pt.join()
        assert_equals(pt.is_alive(), False)


class StoppableExceptionTheadTests(unittest.TestCase):
    def run_with_exception_finishes_test(self):
        """ Subclass StoppableExceptionThread and finish method `run_with_exception` """
        class IncrementThread(StoppableExceptionThread):
            """ Used to test _stop in `run` """
            def __init__(self, *args, **kwargs):
                self.x = args[0]
                StoppableExceptionThread.__init__(self, *args[1:], **kwargs)

            def run_with_exception(self):
                while not self._stop.is_set():
                    with self.x.get_lock():
                        self.x.value += 1
                        if self.x.value > 5:
                            break

        x = Value('i', 0)
        st = IncrementThread(x)
        st.start()
        sleep(1)
        assert_equals(st.stopped, False)
        st.join()
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_equals(x.value, 6)

    def run_with_exception_stop_test(self):
        """ Subclass StoppableExceptionThread and stop method `run_with_exception` """
        class IncrementThread(StoppableExceptionThread):
            """ Used to test _stop in `run` """
            def __init__(self, *args, **kwargs):
                self.x = args[0]
                StoppableExceptionThread.__init__(self, *args[1:], **kwargs)

            def run_with_exception(self):
                while not self._stop.is_set():
                    with self.x.get_lock():
                        self.x.value += 1

        x = Value('i', 0)
        st = IncrementThread(x)
        st.start()
        sleep(1)
        assert_equals(st.stopped, False)
        st.stop()
        assert_equals(st.stopped, True)
        st.join()
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_greater(x.value, 0)

    def run_with_exception_except_test(self):
        """ Subclass StoppableExceptionThread and raise exception in method `run_with_exception` """
        class IncrementThread(StoppableExceptionThread):
            """ Used to test _stop in `run` """
            def __init__(self, *args, **kwargs):
                self.x = args[0]
                StoppableExceptionThread.__init__(self, *args[1:], **kwargs)

            def run_with_exception(self):
                while not self._stop.is_set():
                    with self.x.get_lock():
                        self.x.value += 1
                        if self.x.value > 5:
                            raise ValueError('x > 5')

        x = Value('i', 0)
        st = IncrementThread(x)
        st.start()
        sleep(1)
        assert_equals(st.stopped, False)
        with self.assertRaises(ValueError):
            st.join()
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_equals(x.value, 6)

    def target_finishes_test(self):
        """ run target function """

        def target_sleep(stop_event):
            while not stop_event.is_set():
                stop_event.wait(1)
                return

        st = StoppableExceptionThread(target=target_sleep)
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.join()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), False)

    def target_with_args_finishes_test(self):
        """ run target function with arguments """

        def target_finite(x, stop_event):
            stop_event.wait(0.5)
            while not stop_event.is_set():
                with x.get_lock():
                    x.value += 1
                    if x.value > 5:
                        break

        x = Value('i', 0)
        st = StoppableExceptionThread(target=target_finite, args=(x,))
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.join()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_equals(x.value, 6)

    def target_stop_test(self):
        """ stop running infinite-loop target function """
        def target_infinite(stop_event):
            while not stop_event.is_set():
                stop_event.wait(1)

        x = Value('i', 0)
        st = StoppableExceptionThread(target=target_infinite)
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        st.stop()
        assert_equals(st.stopped, True)
        st.join()
        assert_equals(st.is_alive(), False)

    def target_except_test(self):
        """ propogate exception from target function """
        def target_with_exception(x, stop_event):
            stop_event.wait(0.5)
            while not stop_event.is_set():
                with x.get_lock():
                    x.value += 1
                    if x.value > 5:
                        raise ValueError('x > 5')

        x = Value('i', 0)
        st = StoppableExceptionThread(target=target_with_exception, args=(x,))
        st.start()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), True)
        with self.assertRaises(ValueError):
            st.join()
        assert_equals(st.stopped, False)
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_equals(x.value, 6)
