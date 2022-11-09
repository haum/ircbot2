#!/usr/bin/env python3

import importlib
import pkgutil
import sys
from inspect import signature

from .tasks import tasks_start

class Bot:
    def __init__(self, username, password, chan, server, port):
        print(f'Connection to {chan} on {server}:{port} as {username} with{"" if password else "out"} password')
        self._chan = chan
        self._commands = {}
        self._init_commands()

    def _init_commands(self):
        for _,n,_ in pkgutil.iter_modules(['commands']):
            module = importlib.import_module('commands.' + n)
            if module.command and len(signature(module.command).parameters) == 2:
                self._commands[n] = module
            else:
                print(f'`{n}` command has no `command` function with exactly two arguments', file=sys.stderr)

    def start(self):
        print('Commands: ' + ' '.join(sorted(self._commands.keys())))
        tasks_start(self)

    def msg(self, msg, me=False):
        for msg in msg.split('\n'):
            if me:
                print('ME:', msg)
            else:
                print('MSG:', msg)

