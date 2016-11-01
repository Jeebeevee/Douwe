import asyncio
import re
import time
import imaplib

from cloudbot import hook
import cloudbot

'''

@asyncio.coroutine
@hook.periodic(600, initial_interval=600)
def load_mail(bot):
    conn = bot.connections['scoutlink']
    if not conn.ready:
        return

    mailcnf = bot.config.get('gmail', {})
    mail = {}
    mail['user'] = mailcnf.get('mailuser', None)
    mail['pass'] = mailcnf.get('mailpass', None)
    mail['msgto'] = mailcnf.get('mailmsgto', None)

    mailcount = mailcheck(mail)
    if mailcount != 0:
        conn.message(mail['msgto'], 'Er zijn ' + str(mailcount) + ' ongelezen e-mail op '+ mail['user'])

'''
@hook.command(permissions=["jotico"])
def checkmail(bot, conn, notice):

    mailcnf = bot.config.get('gmail', {})
    mail = {}
    mail['user'] = mailcnf.get('mailuser', None)
    mail['pass'] = mailcnf.get('mailpass', None)
    mail['msgto'] = mailcnf.get('mailmsgto', None)
	
    mailcount = mailcheck(mail)
    if mailcount != 0:
        notice(str(mailcount) + ' ongelezen e-mail op '+ mail['user'])
    else:
        notice('Geen ongelezen mail.')

# de mailchecker
def mailcheck(mail):

	
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(mail['user'], mail['pass'])
    imap.select('INBOX')

    (status, response) = imap.search(None, '(UNSEEN)')
    unread_msg_nums = response[0].split()

    return len(unread_msg_nums)


