#!/usr/bin/env python3

import importlib
import pkgutil
import sys
from inspect import signature

import irc.bot
from irc.client import NickMask

from .tasks import tasks_start

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, password, chan, server, port):
        print(f'Connection to {chan} on {server}:{port} as {username} with{"" if password else "out"} password')
        super().__init__([(server, port)], username, username)
        self._serv = None
        self._username = username
        self._password = password
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

    def on_welcome(self, serv, ev):
        print(f'Connected, join {self._chan}')
        self._serv = serv
        if self._password:
            self._serv.privmsg('nickserv', 'IDENTIFY ' + self._password)
        self._serv.join(self._chan)

    def on_join(self, serv, ev):
        if NickMask(ev.source).nick != self._username: return
        print(f'Channel joined')
        tasks_start(self)

    def on_pubmsg(self, serv, ev):
        message = ev.arguments[0]
        nick = NickMask(ev.source).nick

        if message[0] != '!': return

        chan = self.channels[self._chan]
        if not (chan.is_voiced(nick) or chan.is_halfop(nick) or chan.is_oper(nick)):
            self.msg(f"n'exécute pas les ordres de {nick}", True)
            return

        message_split = message[1:].split()
        cmd = message_split[0]

        if cmd == 'help':
            if len(message_split) > 1:
                if not message_split[1] in self._commands:
                    self.msg(f'ne connaît pas la commande `!{message_split[1]}`', True)
                elif self._commands[message_split[1]].help and len(signature(self._commands[message_split[1]].help).parameters) == 2:
                    self._commands[message_split[1]].help(self, ' '.join(message_split[2:]))
                else:
                    self.msg(f'ne dispose d\'aide pour la commande `!{message_split[1]}`', True)
            else:
                lst = '!'+' !'.join(sorted(self._commands.keys()))
                self.msg('reconnait les commandes: ' + lst, True)
            return

        if not cmd in self._commands.keys():
            self.msg(f'ne comprend pas la commande `!{cmd}`', True)
            return

        self._commands[cmd].command(self, message[len(cmd)+1:].strip())

    def msg(self, msg, me=False):
        if not self._serv: return
        for msg in msg.split('\n'):
            if me:
                self._serv.action(self._chan, msg)
                print('ME:', msg)
            else:
                self._serv.privmsg(self._chan, msg)
                print('MSG:', msg)

