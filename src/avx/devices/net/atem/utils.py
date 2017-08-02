from avx.devices.Device import InvalidArgumentException

import ctypes
import inspect


def byteArrayToString(byteArray):
    return ''.join(chr(b) for b in byteArray)


def bytes_of(val):
    return [(val >> 8), (val & 0xFF)]


class NotInitializedException(Exception):
    pass


def assertTopology(topType, argKey):
    def wrap(func):
        def wrapped_func(self, *args, **kwargs):
            args_dict = inspect.getcallargs(func, self, *args, **kwargs)
            value = args_dict[argKey]

            limit = self._system_config['topology'][topType]

            if value <= 0 or value > limit:
                raise InvalidArgumentException

            return func(self, *args, **kwargs)
        return wrapped_func
    return wrap


def convert_cstring(bs):
    return ctypes.create_string_buffer(str(bs)).value.decode('utf-8')


def parseBitmask(num, labels):
    states = {}
    for i, label in enumerate(labels):
        states[label] = bool(num & (1 << len(labels) - i - 1))
    return states


def requiresInit(func):
    def inner(self, *args, **kwargs):
        if not self._isInitialized:
            raise NotInitializedException()
        return func(self, *args, **kwargs)
    return inner
