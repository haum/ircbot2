#!/usr/bin/env python3

import random
import re
import sqlite3
from datetime import date, datetime
from core.permissions import priviledged

dbpath = '_website/agenda.sqlite'
seances_messages = (
    "Si tu as un projet, viens nous voir et nous en parler !",
    "Si tu aimes bricoler, viens t'amuser avec nous !",
    "Tant que tu n'as pas essayé tu peux encore te passer de nous... VIENS !",
    "Si hacker est pour toi plus qu'un truc qu'on entend aux infos, passe nous voir !",
    "Envie de plancher avec nous à d'autres expériences insolites ?",
)
today = date.today

def help(bot, msg):
    bot.msg('!agenda add <date [J]J/MM[/YYYY] [[H]H:MM]> ["Titre" ["Lieu" [Desciption]]]: Ajouter un évènement')
    bot.msg('!agenda rm <id>: Retirer un évènement')
    bot.msg('!agenda ls [all]: Lister les derniers évènements')

def command(bot, msg, is_privileged):
    if msg == '': msg = 'ls'
    cmd = msg.split()[0]
    if cmd == 'add': cmd_add(bot, msg, is_privileged)
    elif cmd == 'rm': cmd_rm(bot, msg, is_privileged)
    elif cmd == 'ls': cmd_ls(bot, msg, is_privileged)
    elif cmd == 'help': help(bot, '')
    else: bot.msg('ne comprends pas la commande pour l\'agenda.', True)

add_re = re.compile(r'^add\s+'
    r'(\d{1,2}\/\d{2}(\/\d{2,4})?)\s*'
    r'(\d{1,2}:\d{2})?\s*'
    r'("([^"]+)")?\s*'
    r'("([^"]+)")?\s*'
    r'(.*)$')

@priviledged
def cmd_add(bot, msg, is_privileged):
    # add 8/11/2022 16:40 "Titre" "Lieu" Description longue
    # add 8/11/2022 16:40 "Titre" "Lieu"
    # add 8/11/2022 16:40 "Titre"
    # add 8/11/2022 16:40
    # add 8/11/2022 6:40
    # add 8/11/2022
    # add 8/11/22
    # add 8/11
    result = add_re.match(msg)
    if not result: return bot.msg('ne comprend pas la requête', True)
    date, _, hour, _, title, _, location, description = result.groups()
    ds = date.split('/')
    if len(ds) == 2: ds.append(str(today().year))
    if int(ds[2]) < 1000: ds[2] = str(int(ds[2])+2000)
    hs = hour.split(':') if hour else ['21', '00']
    py_date = datetime(int(ds[2]), int(ds[1]), int(ds[0]), int(hs[0]), int(hs[1]))
    date = py_date.isoformat().replace('T', ' ')[:-3]
    if title is None: title = 'Session bidouille'
    if location is None: location = 'Local du HAUM'
    if description == '': description = random.choice(seances_messages)

    db = sqlite3.connect(dbpath)
    db.cursor().execute(
        'INSERT INTO agenda (date, titre, lieu, description, status) '
        'VALUES (?,?,?,?,1)',
        (date, title, location, description))
    db.commit()
    db.close()
    cmd_ls(bot, '', is_privileged, 1)

@priviledged
def cmd_rm(bot, msg, is_privileged):
    try:
        id = int(msg.split()[1])
    except:
        bot.msg('ne comprend pas la requête', True)
        return
    db = sqlite3.connect(dbpath)
    db.cursor().execute('UPDATE agenda SET status=0 WHERE rowid=?', (id,))
    db.commit()
    db.close()
    bot.msg(f'agenda: entrée #{id} retirée')

def cmd_ls(bot, msg, is_privileged, limit=0):
    now = datetime.now().replace(microsecond=0).isoformat().replace('T', ' ')[:-3]
    query = 'SELECT rowid, date, titre, lieu, description FROM agenda WHERE status=1 AND date > "' + now + '" ORDER BY date DESC, rowid DESC'
    ms = msg.split()
    if limit > 0:
        query += ' LIMIT ' + str(limit)
    elif len(ms) <= 1 or ms[1] != 'all':
        query += ' LIMIT 5'

    bot.msg('(id, date, titre, lieu, description)')
    db = sqlite3.connect(dbpath)
    for row in db.cursor().execute(query):
        bot.msg(str(row))
    db.close()

