import sys
from threading import Event, Thread
import Queue


class StoppableThread(Thread):
    """
    Thread with internal stop event.  To properly work, the `run` method or `target` function
    MUST check for changes in the stop event.

    If using `run` method, periodically check if <threading.Event> `self._stop` is set: `self._stop.is_set()`.

    If using `target` argument, a <threading.Event> will be passed in as the last positional argument.
    """
    def __init__(self, *args, **kwargs):
        self._stop = Event()
        if kwargs.get('target') is not None:
            # for threads initialized with a `target` function
            # add stop event as the last calling argument
            kwargs['args'] = kwargs.get('args', tuple()) + (self._stop,)
        super(StoppableThread, self).__init__(*args, **kwargs)

    def stop(self):
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.is_set()


class ExceptionThread(Thread):
    """
    Thread that raises exceptions in the main context.  To properly work, use the
    `run_with_exception` method in place of `run`
    """
    def __init__(self, *args, **kwargs):
        super(ExceptionThread, self).__init__(*args, **kwargs)
        self._status_queue = Queue.Queue()

    def run_with_exception(self):
        """This method should be overriden."""
        raise NotImplementedError

    def run(self):
        """This method should NOT be overriden."""
        try:
            if self._Thread__target:
                super(ExceptionThread, self).run()
            else:
                self.run_with_exception()
        except BaseException:
            self._status_queue.put(sys.exc_info())
        self._status_queue.put(None)

    def join(self, timeout=None):
        super(ExceptionThread, self).join(timeout=timeout)
        try:
            ex_info = self._status_queue.get_nowait()
        except Queue.Empty:
            # Either a timeout or join is being called again
            return
        else:
            if ex_info is None:
                return
            else:
                raise ex_info[1]


class StoppableExceptionThread(StoppableThread, ExceptionThread):
    """
    Thread that can be stopped and propogates exceptions from `join`
    To work properly, `run_with_exception` method or `target` argument
    MUST check for changes in the stop event
    """
    def __init__(self, *args, **kwargs):
        super(StoppableExceptionThread, self).__init__(*args, **kwargs)
        # Set up for ExceptionThread
        self._status_queue = Queue.Queue()
