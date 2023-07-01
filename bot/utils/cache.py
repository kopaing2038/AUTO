from typing import Dict, Union, List
from pyrogram.types import ChatMember


class Cache:
    BANNED: List[int] = []
    CANCEL_BROADCAST: bool = False
    ADMINS: Dict[int, Dict[str, Union[List[int], float, Dict[int, ChatMember]]]] = {}
    USERNAMES = {}
    BUTTONS = {}
    CANCEL = False
    CURRENT = 0
    SEARCH_DATA = {}
    SETTINGS_CACHE = {}
    KEYWORD = {}
    SETTINGS = {}
