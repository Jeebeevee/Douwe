import cloudbot
from cloudbot import hook
from cloudbot.util import database
from cloudbot.util.timeparse import time_parse
from cloudbot.util.timeformat import format_time, time_since

from sqlalchemy import select
from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.types import REAL
from sqlalchemy.exc import IntegrityError

counttable = Table(
    'commandCounter',
    database.metadata,
    Column('chan', String(31)),
    Column('command', String(4)),
    Column('count', String(11)),
    PrimaryKeyConstraint('chan', 'command')
)

global db

def AddCount(usedChannel, usedCommand, db):
    check = select([counttable.c.count]) \
        .where(counttable.c.chan == usedChannel) \
        .where(counttable.c.command == usedCommand) \
        .limit(1)
    #print("{},{}:{}".format(usedChannel,usedCommand,check))
    ChanExist = db.execute(check).fetchall()
    #if len(db.execute(check).fetchall()):
    if len(ChanExist):
        ChanExist = db.execute(check).fetchall()
        counter = int(ChanExist[0]) + 1;
        query = counttable.update() \
            .where(counttable.c.chan == usedChannel) \
            .where(counttable.c.command == usedCommand) \
            .values(count=counter)  
    else:
        query = counttable.insert().values(
            chan=usedChannel,
            command=usedCommand,
            count=1
        )
    db.execute(query)
    db.commit()

@hook.command()
def test(text,event, bot, plugin, message):
    message("{}".format(vars(plugin)))


@hook.sieve()
def CommandCounter(bot, event, db):
    #print("{}".format(vars(bot.db_base)))
    #print("{}".format(event))
    #print("{}".format(plugin))
    if plugin.type == "command":
        usedCommand = event.triggered_command
        usedChannel = event.chan.lower()
        AddCount(usedChannel, usedCommand, db)
    return event

