import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False

@hook.on_start()
def load_foods(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global coffee_data, tea_data, beer_data

    with codecs.open(os.path.join(bot.data_dir, "coffee_nl.json"), encoding="utf-8") as f:
        coffee_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "tea_nl.json"), encoding="utf-8") as f:
        tea_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "beer.json"), encoding="utf-8") as f:
        beer_data = json.load(f)


@asyncio.coroutine
@hook.command(autohelp=False)
def water(text, nick, action):
    """<user> - gives <user> a nice hot chocolatemilk"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "Die kan ik geen water geven."

    action("geeft {} een groot glas koud water!".format(user))


@asyncio.coroutine
@hook.command(autohelp=False)
def port(text, nick, action):
    """<user> - gives <user> a nice hot chocolatemilk"""
    if text != '':
        user = text.strip()
    else:
        user = nick
 
    if not is_valid(user):
        return "Ik kan {} geen port geven. Is die wel meerderjarig?".format(user)

    radar = random.choice([' en geeft er ook een aan Radar', '', ''])

    action("geeft {} een glas port{}!".format(user, radar))



@asyncio.coroutine
@hook.command(autohelp=False)
def choco(text, nick, action):
    """<user> - gives <user> a nice hot chocolatemilk"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "Die kan ik geen chocolademelk geven."

    tempature = random.choice(['warme', 'hete', 'warme', 'warme', 'hete', 'warme', 'warme'])
    cream = random.choice([' met een toefje slagroom', ' met slagroom', '', '', ' met een rietje', ''])

    action("geeft {} een {} chocolademelk{}!".format(user, tempature, cream))

		

@asyncio.coroutine
@hook.command(autohelp=False)
def koekje(text, nick, action):
    """<user> - gives <user> a cookie"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "I can't give a cookie to that user."

    cookie_type = random.choice(['Chocolate Chip ', 'Oreo ', 'Glace ', '', 'stroop', 'Nijntje '])
    size = random.choice(['klein', 'normaal', 'groot', 'enorme'])
    flavor = random.choice(['lekker', 'smerig', 'verrukelijk'])
    method = random.choice(['maakt voor', 'geeft aan', 'koopt voor'])
    side_dish = random.choice(['glas melk', 'kom ijs', 'kom chocolade saus'])

    action("{} {} een {} {} {}koek met een {}!".format(method, user, flavor, size, cookie_type, side_dish))


@asyncio.coroutine
@hook.command(autohelp=False)
def koffie(text, nick, action):
    """<user> - give coffee to <user>"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "I can't give coffee to that user."

    generator = textgen.TextGenerator(coffee_data["templates"], coffee_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
    
   
@asyncio.coroutine
@hook.command(autohelp=False)
def thee(text, nick, action):
    """<user> - give tea to <user>"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "I can't give tea to that user."

    generator = textgen.TextGenerator(tea_data["templates"], tea_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command(autohelp=False)
def bier(text, nick, action):
    """<user> - give beer to <user>"""
    if text != '':
        user = text.strip()
    else:
        user = nick

    if not is_valid(user):
        return "I can't give beer to that user."

    generator = textgen.TextGenerator(beer_data["templates"], beer_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
