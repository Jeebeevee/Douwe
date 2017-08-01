from cloudbot import hook
from cloudbot.util import textgen

import asyncio


@asyncio.coroutine
@hook.command(autohelp=False, permissions=["jotico"])
def test (bot, event, message):
    message("{}".format(event.triggered_command))


@asyncio.coroutine
@hook.sieve()
def MyCommands(bot,event,_hook):
    if _hook.type == "command": #in bot.plugin_manager.commands:
        print("exist: {}".format(event.triggered_command))
        return event
    elif  _hook.type == "event":
        return event
    else:
        print("not exist: {}".format(_hook.type))
        return event