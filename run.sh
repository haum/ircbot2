#!/bin/sh

cd /app
[ -f .env ] && source .env
git pull
python3 irc_bot.py
sleep 1
