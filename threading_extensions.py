import sys
from threading import Event, Thread
import Queue


class StoppableThread(Thread):
    """
    Thread with internal stop event.  To properly work, the `run` method or `target` function
    MUST check for changes in the stop event.  If using `target`, the stop event
    will be passed in as the last argument.
    """
    def __init__(self, *args, **kwargs):
        self._stop = Event()
        if kwargs.get('target') is not None:
            # old style threads run `target` function with arguments `args`
            # add stop_event as the last argument
            kwargs['args'] = tuple(kwargs.get('args', lambda x: list()),) + (self._stop,)
        super(StoppableThread, self).__init__(*args, **kwargs)

    def stop(self):
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.is_set()


class ExceptionThread(Thread):
    """
    Thread that raises exceptions in the main loop.  To properly work, use the
    `run_with_exception` method in place of `run`
    
    Credit for initial implementation: Mateusz Kobos with http://stackoverflow.com/a/6874161/191442
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
            self.run_with_exception()
        except BaseException:
            self._status_queue.put(sys.exc_info())
        self._status_queue.put(None)

    def join(self, timeout=None):
        if self.is_alive():
            super(ExceptionThread, self).join(timeout=timeout)
            ex_info = self._status_queue.get()
        else:
            # thread already finished
            try:
                ex_info = self._status_queue.get_nowait()
            except Queue.Empty:
                ex_info = None
        if ex_info is None:
            return
        else:
            raise ex_info[1]


class StoppableExceptionThread(ExceptionThread, StoppableThread):
    """
    Thread that can be stopped and propogates exceptions from `join`
    To work properly, `run_with_exception` MUST check for changes in the stop event
    
    TODO: add support for `target`/`args` initialization
    """
    def __init__(self, *args, **kwargs):
        """ Set up StoppableThread """
        self._stop = Event()
        super(StoppableExceptionThread, self).__init__(*args, **kwargs)
