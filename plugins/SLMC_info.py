import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

@asyncio.coroutine
@hook.command("mc_ask", autohelp=False)
def ask (text, message):
    message(" If you have a question, please just ask it. Don't look for admins or topic experts. Don't ask to ask or ask if people are awake or available. Just ask the question to the chat straight out, and wait patiently for a reply.")
	
@asyncio.coroutine
@hook.command("mc_roles", autohelp=False)
def roles (text, message):
    message("[Admin] = Administrator, [Mod] = Moderator and [Helper] = Helper.")

@asyncio.coroutine
@hook.command("mc_irc", autohelp=False)
def irc (text, message):
    message("ScoutLink have three services for scouts around the world: IRC (webchat), Teamspeak (voice chat) and Minecraft.")
    message("We've connected Minecraft in-game chat to our #minecraft IRC channel. This means that those people you see with [IRC] in front of their nicks are on then #minecraft IRC channel.")
    message("You can join the channel by going to http://webchat.scoutlink.net/#minecraft")

@asyncio.coroutine
@hook.command("mc_claims", autohelp=False)
def claims (text, message):
    message("There are three ways of trusting another scout in survival claims")
    message("(a) /Trust - Gives another player permission to edit in your claim")
    message("(b) /AccessTrust - Gives a player permission to use your buttons, levers, and beds.")
    message("(c) /ContainerTrust - Gives a player permission to use your buttons, levers, beds, crafting gear, containers, and animals.")


