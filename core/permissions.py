#!/usr/bin/env python3

class PermissionException(BaseException):
    pass

def priviledged(fct):
    def wrap(bot, msg, is_privileged):
        if not is_privileged: raise PermissionException
        fct(bot, msg, is_privileged)
    return wrap
