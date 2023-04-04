#!/bin/sh

export MUSL_LOCPATH=/usr/share/i18n/locales/musl
export LC_ALL=fr_FR.UTF-8

cd /app
[ -f .env ] && source .env
git pull
python3 irc_bot.py
sleep 1
