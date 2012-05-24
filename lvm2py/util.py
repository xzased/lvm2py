from functools import wraps
from .exception import HandleError


size_units = {
    "B":    1,       # byte
    "KB":   1000**1, # kilobyte
    "MB":   1000**2, # megabyte
    "GB":   1000**3, # gigabyte
    "TB":   1000**4, # terabyte
    "PB":   1000**5, # petabyte
    "EB":   1000**6, # exabyte
    "ZB":   1000**7, # zettabyte
    "YB":   1000**8, # yottabyte
    "KiB":  1024**1, # kibibyte
    "MiB":  1024**2, # mebibyte
    "GiB":  1024**3, # gibibyte
    "TiB":  1024**4, # tebibyte
    "PiB":  1024**5, # pebibyte
    "EiB":  1024**6, # exbibyte
    "ZiB":  1024**7, # zebibyte
    "YiB":  1024**8, # yobibyte
    "%":    1        # we've got percents!!!
}

def size_convert(bytes, units):
    size =  float(bytes) / size_units[units]
    return size

def handleDecorator():
    """
    Wraps methods to check if the given lvm
    handle is still active.
    """
    def wrap(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            if self.handle:
                return fn(self, *args, **kwargs)
            raise HandleError("Handle is closed for this instance.")
        return wrapped
    return wrap