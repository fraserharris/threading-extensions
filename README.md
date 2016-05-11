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

Example using `target`, `args` and `kwargs`:

    def infinite_running_target(x, stop_event, y=None):
       # x & y are examples
        while not stop_event.is_set():
            do_something()
            # use this in place of time.sleep b/c wait is interrupted by stop events
            # and will immediately exit
            stop_event.wait(1)
    
    st = StoppableThread(target=infinite_running_target, args=(1,), kwargs={"y": 2})
    st.start()
    assert(st.is_alive() is True)
    assert(st.stopped is False)
    st.stop()
    assert(st.is_alive() is False)
    assert(st.stopped is True)

# ExceptionThread
Thread that propogates exceptions raised in the thread to the main context on `join`.  To properly work using the class method `run`, implement `run_with_exception` method instead.

Example using `run_with_exception`:

    class RaiseThread(ExceptionThread):
        def run_with_exception(self):
            raise ValueError('eep!')
    
    rt = RaiseThread()
    rt.start()
    rt.join() # ValueError: 'eep!'

Example using `target`, `args` and `kwargs`:

    def raises_exception_target(x, y=None):
        # x & y are examples
        raise ValueError('eep!')
    
    et = Thread(target=raises_exception_target, args=(1,), kwargs={"y": 2})
    et.start()
    et.join() # ValueError: 'eep!'

# StoppableExceptionThread
Thread that is both stoppable AND propogates exceptions to the main context on `join`. To properly work using the class method `run`, implement `run_with_exception` method instead.

See above examples.

Happy Threading!
