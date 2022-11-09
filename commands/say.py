#!/usr/bin/env python3

def help(bot, msg):
    bot.msg('!say <something>: Make me say <something>')

def command(bot, msg):
	bot.msg(msg)
