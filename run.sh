#!/bin/bash

export LC_ALL=fr_FR.UTF-8

if [ ! -f /root/.local/bin/uv ]
then
	curl -LsSf https://astral.sh/uv/install.sh | sh
	/root/.local/bin/uv venv /app/venv/
fi

cd /app
source venv/bin/activate
/root/.local/bin/uv pip install irc pelican icalendar piexif pillow
[ -f .env ] && source .env
git pull
python3 irc_bot.py
sleep 5
