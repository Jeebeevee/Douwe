import asyncio
import pymysql.cursors
import re
import time
import random

from cloudbot import hook
import cloudbot

ads = [
"Altijd weer een gezellig moment, Met de lekkerste koffie die je kent. Je bent thuis, waar je Douwe Egberts drinkt.",
"Douwe Egberts koffie: Dat is andere koffie",
"Scoutlink is het hele jaar door open, kom je na de JOTI ook nog is gezellig chatten?",
"Nieuwe vrienden gemaakt tijdens de JOTI? zoek elkaar nog eens op hier op Scoutlink."
]

@hook.command()
def test(conn):
    print(conn.channels)

#@hook.on_start()
#def load_ads(bot,message):
#    adrunner(message)

@asyncio.coroutine
def waittimer(seconds_to_sleep=15):
    yield from asyncio.sleep(seconds_to_sleep)

def adrunner(message):
    waittime = int(random.randint(3,36))
    waittime = waittime * 100
    print(waittime)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(waittimer(int(waittime)))
    message('#dutch01',"{}".format(random.choice(ads)))
    loop.close()
    adrunner(message)