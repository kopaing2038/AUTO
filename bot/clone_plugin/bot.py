
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @SpEcHIDe

from pyrogram import Client, enums, __version__

#from . import API_HASH, APP_ID, LOGGER, BOT_TOKEN 

from bot.clone_plugin.user import User

class Bot(Client):
    USER: User = None
    USER_ID: int = None

    
