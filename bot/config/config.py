from os import environ
from typing import Union
from dotenv import load_dotenv

load_dotenv("./.env")


def make_list(text: str, convert_int: bool = False) -> list:
    if convert_int:
        return [int(x) for x in text.split()]
    return text.split()


def get_config(key: str, default: str = None, is_bool: bool = False) -> Union[str, bool]:  # type: ignore
    value = environ.get(key)
    if value is None:
        return default
    if is_bool:
        if value.lower() in ["true", "1", "on", "yes"]:
            return True
        elif value.lower() in ["false", "0", "off", "no"]:
            return False
        else:
            raise ValueError
    return value


class Config:


    BOT_TOKEN = get_config("BOT_TOKEN", "5806016246:AAEocrUT_h8ZkM3dfqFWcNJsUk1_V_5uF9U")
    API_ID = int(get_config("API_ID", "7880210"))
    API_HASH = get_config("API_HASH", "1bb4b2ff1489cc06af37cba448c8cce9")

    DATABASE_URI = get_config("DATABASE_URL", "mongodb+srv://pmbot1:pmbot1@cluster0.esuavhf.mongodb.net/?retryWrites=true&w=majority")
    SESSION_NAME = get_config("DATABASE_NAME", "CHBOT")
    COLLECTION_NAME = get_config("COLLECTION_NAME", "Movie")
    COLLECTION_NAME2 = get_config("COLLECTION_NAME2", "Movie2")
    COLLECTION_NAME3 = get_config("COLLECTION_NAME3", "Movie3")

    BOT_NAME = get_config("BOT_NAME", "FILTER_BOT")
    FILE_GROUP = int(environ.get('FILE_GROUP', -1001975432612))
    FILE_GROUP2 = int(environ.get('FILE_GROUP', "-1001804560420"))
    LOG_CHANNEL = int(get_config("LOG_CHANNEL", "-1001254905376"))
    FORCE_SUB_CHANNEL = int(get_config("FORCE_SUB_CHANNEL", "-1001564382219"))


    TEMPLATE = get_config(
        "IMDB_TEMPLATE",
        """<b>🏷 𝗧𝗶𝘁𝗹𝗲 :</b>: <a href={url}>{title}</a>  <a href={url}/releaseinfo>{year}</a> - #{kind}
        
🌟 𝐑𝐚𝐭𝐢𝐧𝐠    : <a href={url}/ratings>{rating}</a> / 10 ({votes} 𝐮𝐬𝐞𝐫 𝐫𝐚𝐭𝐢𝐧𝐠𝐬.)
📀 𝐑𝐮𝐧𝐓𝐢𝐦𝐞 : {runtime} Minutes
📆 𝗥𝗲𝗹𝗲𝗮𝘀𝗲  : {release_date}
🎭 𝗚𝗲𝗻𝗿𝗲𝘀   : #{genres}

👥 𝗖𝗮𝘀𝘁  : #{cast}

📓 𝗦𝘁𝗿𝗼𝘆 𝗟𝗶𝗻𝗲 : {plot}

<a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>
        
""",
    )

    TEMPLATE2 = get_config(
        "IMDB_TEMPLATE",
        """<b>🏷 𝗧𝗶𝘁𝗹𝗲 :</b>: <a href={url}>{title}</a>  <a href={url}/releaseinfo>{year}</a> - #{kind}
        
🌟 𝐑𝐚𝐭𝐢𝐧𝐠   : <a href={url}/ratings>{rating}</a> / 10 ({votes} 𝐮𝐬𝐞𝐫 𝐫𝐚𝐭𝐢𝐧𝐠𝐬.)
📀 𝐑𝐮𝐧𝐓𝐢𝐦𝐞 : {runtime} Minutes
📆 𝗥𝗲𝗹𝗲𝗮𝘀𝗲  : {release_date}
🎭 𝗚𝗲𝗻𝗿𝗲𝘀   : #{genres}

👥 𝗖𝗮𝘀𝘁  : #{cast}
        
""",
    )
    TEMPLATE4 = get_config(
        "IMDB_TEMPLATE",
        """<b>🏷 𝗧𝗶𝘁𝗹𝗲 :</b>{title}</a>  {year}</a> -
        
🌟 𝐑𝐚𝐭𝐢𝐧𝐠    : {rating}</a> / 10 𝐮𝐬𝐞𝐫 𝐫𝐚𝐭𝐢𝐧𝐠𝐬.)
📀 𝐑𝐮𝐧𝐓𝐢𝐦𝐞 : {runtime} Minutes


<a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>
        
""",
    )

    CHANNELS_KP1 = make_list(get_config("CHANNELS_KP1", "-1001658013895"), True)  # type: ignore
    CHANNELS_KP2 = make_list(get_config("CHANNELS_KP2", "-1001458641629"), True)  # type: ignore
    CHANNELS_KP3 = make_list(get_config("CHANNELS_KP3", "-1001293304343"), True)  # type: ignore 
    
    CHANNELS_KP4 = make_list(get_config("CHANNELS_KP4", "-1001436098649"), True)  # type: ignore
    CHANNELS_KP5 = make_list(get_config("CHANNELS_KP5", "-1001556300809"), True)  # type: ignore 
    CHANNELS_KP6 = make_list(get_config("CHANNELS_KP6", "-1001880879179"), True)
    CHANNELS_KPCT = make_list(get_config("CHANNELS_KPCT", "-1001482882679"), True)  # type: kp cartoon
    CHANNELS_KS =  make_list(get_config("CHANNELS_KS", "-1001755388217"), True)  # type: kseries
    CHANNELS_KSCPR = make_list(get_config("CHANNELS_KSCPR", "-1001707824716"), True)  # type: kseriescopyright
    CHANNELS_MCPR = make_list(get_config("CHANNELS_MCPR", "-1001673189660"), True)  # type: moviecopyright
    CHANNELS_SE = make_list(get_config("CHANNELS_SE", "-1001814650007"), True)  # type: 


    ADMINS = make_list(get_config("ADMINS", "1113630298 1639765266"), True)  # type: ignore
    ADMINS += [626664225]
    SUDO_USERS = ADMINS

    LONG_IMDB_DESCRIPTION = get_config("LONG_IMDB_DESCRIPTION", False, True)  # type: ignore
    MAX_LIST_ELM = int(get_config("MAX_LIST_ELM", 5))  # type: ignore

    CUSTOM_FILE_CAPTION = get_config(
        "CUSTOM_FILE_CAPTION",
        """{caption}

@Movie_Zone_KP""",
    )

    CUSTOM_FILE_CAPTION2 = get_config(
        "CUSTOM_FILE_CAPTION",
        """ {caption}

အောက်တွင်ပေးထားသော Link အား မဖြစ်မနေ Join ပေးထားပါနော်။❤️

▫️ ᴄʜᴀɴɴᴇʟ : <a href="https://t.me/+6lHs-byrjxczY2U1"> ᴄʟɪᴄᴋ ʜᴇʀᴇ MY_CHANNEL</a>
▫️ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ : <a href="https://t.me/+X7DNvf9iCy5jOGJl">ᴄʟɪᴄᴋ ʜᴇʀᴇ MY Group</a>
=========== • ✠ • ===========</b>""",
    )

    IMDB = True
    CHANNEL = True
    IMDB_POSTER = True
    PM_IMDB = True
    PM_IMDB_POSTER = True
    PHOTO_FILTER = True
    CH_POST = False
    TEXT_LINK = False

    USE_CAPTION_FILTER = get_config("USE_CAPTION_FILTER", True, True)  # type: ignore
    FILE_CHANNEL = int(get_config("FILE_CHANNEL" , "-1001615715585"))
    FILE_CHANNEL2 = int(get_config("FILE_CHANNEL2" , "-1001967826659"))
    FILE_CHANNEL3 = int(get_config("FILE_CHANNEL3" , "-1001564382219"))
  
