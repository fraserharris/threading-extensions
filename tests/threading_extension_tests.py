from multiprocessing import Value
from nose.tools import assert_equals, assert_greater
from time import sleep
import unittest

from threading_extensions import StoppableThread, ExceptionThread, StoppableExceptionThread


class StoppableThreadTests(unittest.TestCase):
    def stop_target_test(self):
        """ Stop target function """
        def run_in_stoppable_thread(x, stop_event):
            while not stop_event.is_set():
                with x.get_lock():
                    x.value += 1

        x = Value('i', 0)
        st = StoppableThread(target=run_in_stoppable_thread, args=(x,))
        st.start()
        sleep(1)
        assert_equals(st.stopped, False)
        st.stop()
        assert_equals(st.stopped, True)
        st.join()
        assert_equals(st.is_alive(), False)
        with x.get_lock():
            assert_greater(x.value, 0)

    def stop_run_test(self):
        """ Subclass StoppableThread and stop method `run` """
        class IncrementThread(StoppableThread):
            """ Used to test _stop in `run` """
            def __init__(self, *args, **kwargs):
                self.x = args[0]
                StoppableThread.__init__(self, *args[1:], **kwargs)

            def run(self):
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
        pt = self.PassThread()
        pt.start()
        pt.join()
        assert_equals(pt.is_alive(), False)
        pt.join() # join must know that thread is already dead
        assert_equals(pt.is_alive(), False)


class StoppableExceptionTheadTests(unittest.TestCase):
    def run_test(self):
        """ Subclass StoppableThread and run method `run_with_exception` 10 times """
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

    def stop_run_test(self):
        """ Subclass StoppableThread and stop method `run_with_exception` """
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

    def stop_run_test(self):
        """ Subclass StoppableThread and stop method `run_with_exception` """
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
