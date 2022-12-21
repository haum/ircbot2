#!/usr/bin/env python3
from core.permissions import priviledged

def help(bot, msg):
    bot.msg('!say <something>: Make me say <something>')

@priviledged
def command(bot, msg, is_privileged):
	bot.msg(msg)
