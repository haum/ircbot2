#!/usr/bin/env python3

import subprocess
import sys
from threading import Thread

def help(bot, msg):
    bot.msg('!up_site: Update website from repo')

worker = None
def command(bot, msg):
    global worker
    if worker and worker.is_alive():
        bot.msg('est en train de reconstruire le site.', True)
    else:
        worker = Thread(target=update_thread_run, args=(bot,))
        worker.start()

def shrun(cmd):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    ret = p.wait() == 0
    if not ret:
        print('\n'.join(s.decode('utf-8') for s in p.stderr.readlines()), file=sys.stderr)
    return ret

def update_thread_run(bot):
    bot.msg('Mise à jour du site...')

    # Clone a local copy if not there
    if not shrun('[ -d _website ] || (git clone https://github.com/haum/website.git _website && git clone https://github.com/haum/website-content.git _website/content/)'):
        bot.msg('Erreur lors du clonage du site.')
        return

    # Update website engine
    if not shrun('cd _website && git pull'):
        bot.msg('Erreur lors de la mise à jour du moteur du site.')
        return

    # Update website content
    if not shrun('cd _website/content && git pull'):
        bot.msg('Erreur lors de la mise à jour du contenu du site.')
        return

    # Build site
    if not shrun('cd _website && rm -rf cache && make publish'):
        bot.msg('Et voilà, tu as encore cassé le site !')
        return

    # Rsync output
    if not shrun('cd _website && rsync -ac --delete ./output/ /www/haum.org/'):
        bot.msg('Erreur lors de la copie finale du site.')
        return

    # End
    bot.msg('Site à jour.')
