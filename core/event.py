class Event():
    _connected_functions = []
    
    def connect(self, func):
        # Can be used as a decorator or called on already existing functions.
        self._connected_functions.append(func)
        return func

    def disconnect(self, func):
        if func in self._connected_functions:
            self._connected_functions.remove(func)

    def call(self, *args, **kwargs):
        for func in self._connected_functions:
            func(*args, **kwargs)