from functools import wraps
from threading import Thread
from typing import Callable
import traceback

from gi.repository import GLib

class Async(Thread):

    def __init__(self, target: Callable | None = None, callback: Callable | None = None, *args, **kwargs) -> None:

        def handler(*args, **kwargs) -> None:
            result, error = None, None
            try: result = target(*args, **kwargs)
            except Exception as e: error = e
            if error: traceback.print_exception(error)
            if callback: callback(result, error)

        super().__init__(target=handler, args=args, kwargs=kwargs, daemon=True)

        self.start()

    @staticmethod
    def function(func: Callable) -> Callable:
        def inner(*args, **kwargs): 
            Async(func, None, *args, **kwargs)
        return inner

def glib_idle(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs: args += tuple([value for _, value in kwargs])
        GLib.idle_add(func, *args)
    return wrapper