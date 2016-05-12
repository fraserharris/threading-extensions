# threading_extensions
Some useful, well-tested extensions of [threading.Thread](https://docs.python.org/2/library/threading.html#thread-objects).  Tested for Python 2.7.

## StoppableThread
Thread with internal stop event.  To properly work, the `run` method or `target` function MUST check for changes in the stop [threading.Event](https://docs.python.org/2/library/threading.html#event-objects).
- If using `run` class method, periodically check if <threading.Event> `self._stop` is set: `self._stop.is_set()`
- If using `target` function keyword argument, the stop `threading.Event` will be passed in as the *last* positional argument.

#### Example using `run`:

    class DoSomethingThread(StoppableThread):
        def run(self):
            # self._stop is an instance of <threading.Event>
            while not self._stop.is_set():
                do_something()
                # use `_stop.wait` in place of `time.sleep` b/c wait is interrupted
                # by the event being set and will immediately exit
                self._stop.wait(10)
    
    dt = DoSomethingThread()
    dt.start()
    
    assert(dt.is_alive() is True)
    assert(dt.stopped is False) # stopped is a property
    
    dt.stop() # sets the stop event in the thread
    dt.join() # wait until thread returns
    
    assert(dt.is_alive() is False)
    assert(dt.stopped is True)

#### Example using `target`, `args` and `kwargs`:

    def infinite_running_target(x, stop_event, y=None):
       # x & y are examples
        while not stop_event.is_set():
            do_something()
            # use `stop_event.wait` in place of `time.sleep` b/c wait is interrupted by
            # stop being set and will immediately exit the wait
            stop_event.wait(1)
    
    st = StoppableThread(target=infinite_running_target, args=(1,), kwargs={"y": 2})
    st.start()
    
    assert(st.is_alive() is True)
    assert(st.stopped is False)
    
    st.stop()
    st.join()
    
    assert(st.is_alive() is False)
    assert(st.stopped is True)

## ExceptionThread
Thread that propogates exceptions raised in the thread to the main context on `join`.  To properly work using the class method `run`, implement `run_with_exception` method instead.

#### Example using `run_with_exception`:

    class RaiseThread(ExceptionThread):
        def run_with_exception(self):
            raise ValueError('eep!')
    
    rt = RaiseThread()
    rt.start()
    rt.join() # ValueError: 'eep!', with complete stack trace

#### Example using `target`, `args` and `kwargs`:

    def raises_exception_target(x, y=None):
        # x & y are examples
        raise ValueError('eep!')
    
    et = Thread(target=raises_exception_target, args=(1,), kwargs={"y": 2})
    et.start()
    et.join() # ValueError: 'eep!', with complete stack trace
    
    assert(et.is_alive() is False)

## StoppableExceptionThread
Thread that is both stoppable AND propogates exceptions to the main context on `join`. To properly work using the class method `run`, implement `run_with_exception` method instead.

See above examples.

# Installation
`pip install https://github.com/fraserharris/threading-extensions/archive/master.zip`

Happy Threading!
