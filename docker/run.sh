#!/bin/sh

docker run --name haum-irc-bot -d --restart always -v /var/haum_irc_bot:/app haum/irc_bot
