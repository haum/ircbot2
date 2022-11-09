#!/usr/bin/env python3

import importlib
import pkgutil
import sys
from inspect import signature
from threading import Thread

tasks_list = []

def tasks_start(bot):
    for _,n,_ in pkgutil.iter_modules(['tasks']):
        module = importlib.import_module('tasks.' + n)
        if module.thread_run and len(signature(module.thread_run).parameters) == 1:
            tasks_list.append(Thread(target=module.thread_run, args=(bot,)))
        else:
            print(f'`{n}` task has no `thread_run` function with only one argument', file=sys.stderr)
    for thread in tasks_list:
        thread.start()

def tasks_join():
    for thread in tasks_list:
        thread.join()
