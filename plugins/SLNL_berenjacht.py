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

#loop tijd voor jacht. 1ste = aanmeldtijd, 2de = cooldowntijd
#runtime = [300,300] 
dieren = ['Beer', 'Tijger', 'Eekhoorn', 'Muis', 'Spin']

bjtable = Table(
    'berenjacht',
    database.metadata,
    Column('chan', String(31)),
    Column('nick', String(31)),
    Column('points', String(32)),
    Column('words', String(32)),
    PrimaryKeyConstraint('chan', 'nick')
)

gametable = Table(
    'berenjachtgame',
    database.metadata,
    Column('chan', String(31)),
    Column('nick', String(31)),
    Column('points', String(32)),
    PrimaryKeyConstraint('chan', 'nick')
)

activetable = Table(
    'berenjachtactive',
    database.metadata,
    Column('chan', String(31)),
    Column('runtime', String(4)),
    Column('downtime', String(4)),
    Column('nick', String(31)),
    Column('time', DateTime),
    Column('active', String(5), default=1),
    PrimaryKeyConstraint('chan')
)

jachtrun = []
jachtcooldown = []

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@asyncio.coroutine
def jachttimer(seconds_to_sleep=15):
    #print('start: {}'.format(seconds_to_sleep))
    yield from asyncio.sleep(seconds_to_sleep)


def gamepoints(chan, nick, points, db, message):
    get_user = select([gametable.c.points]) \
        .where(gametable.c.chan == chan) \
        .where(gametable.c.nick == nick.lower()) \
        .limit(1)
    userdata = db.execute(get_user).fetchall()
    if len(userdata):
        query = gametable.update() \
            .where(gametable.c.chan == chan) \
            .where(gametable.c.nick == nick.lower()) \
            .values(points=points)  
    else:
        query = gametable.insert().values(
            chan=chan,
            nick=nick.lower(),
            points=points
        )
    db.execute(query)
    db.commit()
	
def gamescore(chan, db):
    #bereken de winnaars en hun score
    winners = []
    player_data = select([gametable.c.nick, gametable.c.points]) \
        .where(gametable.c.chan == chan)
    playerdata = db.execute(player_data).fetchall()


    playercount = len(playerdata)
    if playercount >= 30 :
        chances = 66
        winningratio = 1
    elif playercount < 30 and playercount >= 20:
        chances = 35 + playercount
        winningratio = 1
    else:
        chances = 35 + playercount
        if playercount < 20 and playercount >= 10:
            winningratio = 2
        elif playercount < 10:
            winningratio = 3
    #print("spelers: {}, kans: {}, ratio: {}".format(playercount, chances, winningratio))
    for player in playerdata:
        user, bet = player
		
        user_data = select([bjtable.c.points]) \
            .where(bjtable.c.chan == chan) \
            .where(bjtable.c.nick == user.lower()) \
            .limit(1)
        userdata = db.execute(user_data).fetchall()
        points = userdata[0][0]
        randomnumber = random.random() * 100
        #print("user: {}, randomnumber: {}".format(user, randomnumber))
        if randomnumber <= chances:
            winners.append(user)
            newpoints = int(points) + int(winningratio) * int(bet)
            query = bjtable.update() \
                .where(bjtable.c.chan == chan) \
                .where(bjtable.c.nick == user.lower()) \
                .values(points=newpoints)
            db.execute(query)
            db.commit()
    return winners

@asyncio.coroutine
@hook.irc_raw('PRIVMSG')
def pointer (irc_raw, nick, chan, db):
    #telt punten uit de tekst en telt die bij de bestaande punten op
	# command_prefix

    complete = irc_raw[1:].split(':',1) #Parse the message into useful data              
    info = complete[0].split(' ') #all sender info
    text = complete[1] # message

    words = len(text.split())
    points = int(words / 3)
    if points > 15 :
        points = 15
    get_user = select([bjtable.c.points, bjtable.c.words]) \
        .where(bjtable.c.chan == chan) \
        .where(bjtable.c.nick == nick.lower()) \
        .limit(1)
    userdata = db.execute(get_user).fetchall()
    if len(userdata):
        #if oldwords is not '' and oldpoints is not '': # and userdata[1] is not None:
        oldpoints, oldwords = userdata[0]
        #print("{}: {} - {}".format(nick, oldwords, oldpoints))
        points = points + int(oldpoints)
        words = words + int(oldwords)
        query = bjtable.update() \
            .where(bjtable.c.chan == chan) \
            .where(bjtable.c.nick == nick.lower()) \
            .values(points=points, words=words)
    else:
        #print("{}: {} - {}".format(nick, points, words))
        query = bjtable.insert().values(
            chan=chan,
            nick=nick.lower(),
            points=points,
            words=words
        )

    db.execute(query)
    db.commit()


@asyncio.coroutine
@hook.command()
def punten (text, nick, chan, db, message):
    #geeft aantal punten van aanvrager (eventueel met rang)
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        message("{} is geen correcte naam.".format(user))

    get_points = select([bjtable.c.points]) \
        .where(bjtable.c.chan == chan) \
        .where(bjtable.c.nick == user.lower()) \
        .limit(1)
    pointsdata = db.execute(get_points).fetchall()
    if len(pointsdata):
        points = pointsdata[0][0]
        message("{} heeft al {} punten verdient in dit kanaal.".format(user, points))
    else:
        message("Helaas, {} heeft nog geen punten gescored in dit kanaal. Het wordt tijd dat je wat meer gaat praten.".format(user))


@hook.command()
def jacht (text, nick, chan, db, message, notice):
    global jachtrun
    global jachtcooldown
    #Start de bankheist, verzamel deelnemers, time de tijd, geef uitslag
    #print (jachtrun)
    user_data = select([bjtable.c.points]) \
        .where(bjtable.c.chan == chan) \
        .where(bjtable.c.nick == nick.lower()) \
        .limit(1)
    userpoints = db.execute(user_data).fetchall()
    query = select([activetable.c.runtime, activetable.c.downtime]) \
        .where(activetable.c.chan == chan) \
        .where(activetable.c.active == 1) \
        .limit(1)
    chanactive = db.execute(query).fetchall()
    if not len(chanactive):
       message("De jacht is momenteel niet mogelijk")
    elif text == '':
        message("{}, Om mee te doen met de jacht moet een punten aantal opgeven. Met !punten kun je je punten aantal zien.".format(nick))
    elif not RepresentsInt(text):
       message("{}, Foei. en nu een rond getal.".format(nick))
    elif int(text) > 1337:
       message("{}, je kunt niet meer dan 1337 punten inzetten.".format(nick))
    elif int(text) > int(userpoints[0][0])/2:
       message("{}, je kunt niet meer dan de helft van je punten inzetten dan. Je hebt {} punten.".format(nick, userpoints[0][0]))
    elif int(text) < 0 :
       message("{}, het is niet mogelijk om een negatief getal in te vullen.".format(nick))
    elif int(text) == 0 :
       message("{}, nul is geen waarde, dat is een eigenschap.".format(nick))
    else:
        if chan in jachtrun and chan not in jachtcooldown:
            # de jacht draait meld deelnemers aan.
            #message('jacht draait, deelnemen maar.')
            gamepoints(chan, nick, text, db, message)
            notice("Je punten zijn ingezet.", nick)
        elif chan not in jachtrun and chan in jachtcooldown: 
            # jacht is gestopt, nieuwe mag nog niet gestart.
           message('De jacht is afgelopen. We moeten even wachten voor we weer op jacht kunnen.')
        else:
            # er draait geen jacht, nieuwe starten
            jachtrun.append(chan)
            jachtdier = random.choice(dieren)
            runtime, downtime = chanactive[0]
            message("De jacht op een {} is gestart door {}. Ga je mee op jacht?".format(jachtdier, nick))
            runtimemin = int(runtime)/60
            downtimemin = int(downtime)/60
            message("Je hebt {} minuten om je aan te melden.".format(int(runtimemin)))
            gamepoints(chan, nick, text, db, message)
            #print("run: {} cooldown: {}".format(jachtrun, jachtcooldown))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(jachttimer(int(runtime))) #eerste run, men kan deelnemen.
            #nu gaan we zien wie er gaat winnen.
            winner = gamescore(chan, db)
            if len(winner) > 1:
                message("De {0} is geschoten, ik herhaal, de {0} is geschoten.".format(jachtdier))
                winnerstring = ', '.join(winner)
                message("De winnaars zijn {}.".format(winnerstring))
            elif len(winner) == 1:
                message("De {0} is geschoten, ik herhaal, de {0} is geschoten.".format(jachtdier))
                message("De winnaar is {}. ".format(winner[0]))
            else:
                message("Helaas. We hebben de {} niet geschoten. Hij is terug in zijn hol. We zullen moeten wachten tot hij weer tevoorschijn wil komen.".format(jachtdier))
            message("Over {} minuten kunnen we weer op jacht.".format(int(downtimemin)))

			#clean Database / remove players of an channel
            query = gametable.delete() \
                .where(gametable.c.chan == chan)
            db.execute(query)
            db.commit()
            jachtrun.remove(chan)
            jachtcooldown.append(chan)
            #print("run: {} cooldown: {}".format(jachtrun, jachtcooldown))
            loop.run_until_complete(jachttimer(int(downtime))) #cooldown tijd
            jachtcooldown.remove(chan)
            loop.close()
            message("We mogen weer op jacht, wie gaat ons voor in onze jacht en starten de jacht en wie doen er mee?")


@hook.command('jachtadmin','ja', permissions=['jachtgame'])
def jachtadmin (text, nick, db, message):
    input = text.split(' ')

    current_epoch = time.time()
    current_time = datetime.fromtimestamp(current_epoch)

    if input[0] == 'aan' and len(input) == 4:
        state, channel, runtime, downtime = input
        query = select([activetable.c.active]) \
            .where(activetable.c.chan == channel) \
            .limit(1)
        chanactive = db.execute(query).fetchall()
        if len(chanactive) :
            query = activetable.update() \
                .where(activetable.c.chan == channel) \
                .values(runtime=runtime, downtime=downtime, nick=nick, time=current_time, active=1)
        else:
            query = activetable.insert().values(
                chan=channel,
                runtime=runtime,
                downtime=downtime,
                nick=nick.lower(),
				time=current_time,
                active=1
            )
        db.execute(query)
        db.commit()
        message("De Jacht staat nu aan in {}, looptijd: {} sec, wachttijd: {} sec. Ingesteld door: {}".format(channel, runtime, downtime, nick))
    elif input[0] == 'uit':
        state, channel = input
        query = select([activetable.c.active]) \
            .where(activetable.c.chan == channel) \
            .where(activetable.c.active == 1) \
            .limit(1)
        chanactive = db.execute(query).fetchall()
        if len(chanactive) :
            query = activetable.update() \
                .where(activetable.c.chan == channel) \
                .values(nick=nick, time=current_time, active=0)
            db.execute(query)
            db.commit()
            message("De Jacht is uitgezet in {} door {}.".format(channel, nick))
        else:
            message("Er draait geen Jacht in {}".format(channel))
    elif input[0] == 'status':
        query = select([activetable.c.chan, activetable.c.runtime, activetable.c.downtime]) \
            .where(activetable.c.active == 1)
        chandata = db.execute(query).fetchall()
        message("De Jacht is actief in de volgende kanalen met de volgende instellingen:")
        for chanrow in chandata:
            chan, runtime, downtime = chanrow
            message("Kanaal: {}, looptijd: {} sec, wachttijd: {} sec".format(chan, runtime, downtime))
    elif input[0] == 'edit':
        print('EDIT')
    else:
        message("Je moet extra waardes meegeven bij dit commando (aan, uit of edit).")
        message("Aanzetten via !jachtadmin|!ja aan <kanaal> <looptijd in sec> <wachttijd in sec>")
        message("Uitzetten via !jachtadmin|!ja uit <kanaal>")
        message("Jacht status via !jachtadmin|!ja status")
        message("Punten aantal gebruiker aanpassen !jachtadmin|!ja edit <nick> <nieuwe punten>")

