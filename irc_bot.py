#!/usr/bin/env python3

# Simple IRC bot for HAUM

import os
from core import Bot, tasks_join

bot = Bot(
    username = os.getenv('IRCBOT_USERNAME', 'ircbot'),
    password = os.getenv('IRCBOT_PASSWORD', None),
    chan = os.getenv('IRCBOT_CHAN', None),
    server = os.getenv('IRCBOT_SERVER', 'irc.libera.chat'),
    port = os.getenv('IRCBOT_PORT', 6667),
)

try:
	bot.start()
except KeyboardInterrupt:
	bot.die('Bye')

tasks_join()
