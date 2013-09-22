"""
    Defining some Error base classes
"""

class MultipleError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NotFoundError(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

"""
    settings.py related exceptions
"""
class MultipleSettingError(MultipleError):
    def __str__(self):
        out = repr(self.value)
        out = out + "\ntry running with --settings"
        return out

class NoSettingsError(NotFoundError):
    def __str__(self):
        if not self.msg:
            return "settings.py not found"
        
"""
    wsgi.py related exceptions
"""
class MultipleWSGIError(MultipleError):
    def __str__(self):
        out = repr(self.value)
        out = out + "\ntry running with --wsgi"
        return out

class NoWSGIError(NotFoundError):
    def __str__(self):
        if not self.msg:
            return "wsgi.py not found"

"""
    manage.py related exceptions
"""
class MultipleMANAGEError(MultipleError):
    def __str__(self):
        out = repr(self.value)
        out = out + "\ntry running with --manage"
        return out


class NoMANAGEError(NotFoundError):
    def __str__(self):
        if not self.msg:
            return "manage.py not found"


