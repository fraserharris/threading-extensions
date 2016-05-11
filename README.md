# threading-extensions
Some useful, well-tested extensions of threading.Thread

# StoppableThread
Thread with internal stop event.  To properly work, the `run` method or `target` function MUST check for changes in the stop event.  If using `target`, the stop event will be passed in as the last argument.

Example using `run`:

    class DoSomethingThread(StoppableThread):
        def run(self):
            while not self._stop.is_set():
                do_something()
                # use this in place of time.sleep b/c wait is interrupted by stop events
                # and will immediately exit
                self._stop.wait(10)
    
    dt = DoSomethingThread()
    dt.start()
    assert(dt.is_alive() is True)
    assert(dt.stopped is False)
    dt.stop()
    assert(dt.is_alive() is False)
    assert(dt.stopped is True)

Example using `target` and `args`:

    def run_in_stoppable_thread(stop_event):
        while not stop_event.is_set():
            do_something()
            # use this in place of time.sleep b/c wait is interrupted by stop events
            # and will immediately exit
            stop_event.wait(10)
    
    st = StoppableThread(target=run_in_stoppable_thread, args=(,))
    st.start()
    assert(st.is_alive() is True)
    assert(st.stopped is False)
    st.stop()
    assert(st.is_alive() is False)
    assert(st.stopped is True)

# ExceptionThread
Thread that propogates exceptions raised in the thread to the main context on `join`.  To properly work, use the `run_with_exception` method in place of `run`.

Example:

    class RaiseThread(ExceptionThread):
        def run_with_exception(self):
            raise ValueError('eep!')
    
    rt = RaiseThread()
    rt.start()
    rt.join() # ValueError: 'eep!'

# StoppableExceptionThread
Thread that is both stoppable AND propogates exceptions to the main context on `join`. To properly work, use the `run_with_exceptions` method in place of `run`.

See above examples.

TODO: enable `target` and `args` initialization in place of `run_with_exceptions`.
