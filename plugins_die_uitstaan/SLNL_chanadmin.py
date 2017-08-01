from datetime import datetime

import asyncio
import random
import re
import time

import cloudbot
from cloudbot import hook
from cloudbot.util import database
from cloudbot.util.timeparse import time_parse
from cloudbot.util.timeformat import format_time, time_since

from sqlalchemy import select
from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.types import REAL
from sqlalchemy.exc import IntegrityError

adminchan = 'Jeebeevee'
channelinfo = []

channeltable = Table(
    'channelmonitor',
    database.metadata,
    Column('chan', String(31)),
    Column('users', String(4)),
    Column('ops', String(255)),
    Column('mode', String(31)),
    PrimaryKeyConstraint('chan')
)

@asyncio.coroutine
@hook.periodic(30, initial_interval=30)
def ChanInfoRunner (bot):
    conn = bot.connections['scoutlink']
    if not conn.ready:
        return
    for kanaal in conn.channels:
        kanaal = kanaal.split(' ')[0]
        conn.cmd("NAMES", kanaal)
        conn.cmd("MODE", kanaal)

@asyncio.coroutine
@hook.irc_raw('353')
def UsersInChannel(irc_paramlist, conn=None, bot=None, db=None):
    kanaal = irc_paramlist[2].lower()
    names = irc_paramlist[3].split(' ')
    namesnum = len(names)
    ops = []
    for name in names:
        if name[:1] == '@':
            ops.append(name)
    opsstr = str(ops) 

    ChanCheck = select([channeltable.c.chan]) \
        .where(channeltable.c.chan == kanaal) \
        .limit(1)
    ChanExist = db.execute(ChanCheck).fetchall()
    if len(ChanExist):
        query = channeltable.update() \
            .where(channeltable.c.chan == kanaal) \
            .values(users=namesnum, ops=opsstr)  
    else:
        query = channeltable.insert().values(
            chan=kanaal,
            users=namesnum,
            ops=opsstr
        )

    db.execute(query)
    db.commit()
	
@asyncio.coroutine
@hook.irc_raw('324')
def ChannelModes (irc_paramlist, conn=None, bot=None, db=None):
    kanaal = irc_paramlist[1]
    mode = irc_paramlist[2]
    ChanMode = select([channeltable.c.chan]) \
        .where(channeltable.c.chan == kanaal) \
        .limit(1)
    ChanModeExist = db.execute(ChanMode).fetchall()
    if len(ChanModeExist):
        query = channeltable.update() \
            .where(channeltable.c.chan == kanaal) \
            .values(mode=mode)  
    else:
        query = channeltable.insert().values(
            chan=kanaal,
            mode=mode
        )
    db.execute(query)
    db.commit()
		
@asyncio.coroutine
@hook.command('overzicht', 'oz', permissions=['jotico'])
def overzicht (bot, conn, message, db):
    message("Kanaal overzicht:")
    Channels = db.execute(channeltable.select()).fetchall()
    for kinfo in Channels:
        #if kinfo['chan'] is not adminchan:
        ops = eval(kinfo['ops'])
        opsstr = ', '.join(ops)
        message("{}: {} users. {} ops; {}".format(kinfo['chan'], int(kinfo['users'])-1, len(ops), opsstr, adminchan))

