import re
from os import environ
from typing import Union
from dotenv import load_dotenv
from typing import List
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


    BOT_TOKEN = get_config("BOT_TOKEN", "5482704567:AAH4hOppkPz71lO4MePmSw5kbkHGkWYzVKE")
    API_ID = int(get_config("API_ID", "7880210"))
    API_HASH = get_config("API_HASH", "1bb4b2ff1489cc06af37cba448c8cce9")
    DATABASE_URL = get_config("DATABASE_URL", "")
    DATABASE_URI = get_config("DATABASE_URL", "mongodb+srv://pmbot1:pmbot1@cluster0.esuavhf.mongodb.net/?retryWrites=true&w=majority")
    SESSION_NAME = get_config("DATABASE_NAME", "CH11BOT")
    COLLECTION_NAME = get_config("COLLECTION_NAME", "Movie")
    COLLECTION_NAME2 = get_config("COLLECTION_NAME2", "Movie2")
    COLLECTION_NAME3 = get_config("COLLECTION_NAME3", "Movie3")
    COLLECTION_NAME4 = get_config("COLLECTION_NAME4", "Movie4")

    BOT_NAME = get_config("BOT_NAME", "FILTER_BOT")
    FILE_GROUP = int(environ.get('FILE_GROUP', -1001975432612))
    FILE_GROUP2 = int(environ.get('FILE_GROUP', "-1001804560420"))
    LOG_CHANNEL = int(get_config("LOG_CHANNEL", "-1001254905376"))
    FORCE_SUB_CHANNEL = int(get_config("FORCE_SUB_CHANNEL", "-1001161641413"))

    UPDATES_CHANNEL = int(environ. get('UPDATES_CHANNEL', '-1001646572603'))
    #BANNED_CHANNELS = list(set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1001362659779")).split()))
    BIN_CHANNEL = int(environ. get('BIN_CHANNEL', '-1001965839568'))

    FLOOD = int(environ.get("FLOOD", "10"))
    RENAME_MODE = bool(environ.get("RENAME_MODE"))
  
    PICS = (get_config('PICS', 'https://graph.org/file/10337fadbffa79c148340.jpg https://graph.org/file/d36571680767216fc2087.jpg https://graph.org/file/d0c149634f817daadfa7f.jpg https://graph.org/file/25f15ce7d53d0e3e751a5.jpg')).split()
    TEMPLATE = get_config(
        "IMDB_TEMPLATE",
        """<b>🏷 𝗧𝗶𝘁𝗹𝗲 :</b>: <a href={url}>{title}</a>  <a href={url}/releaseinfo>{year}</a> - #{kind}
        
🌟 𝐑𝐚𝐭𝐢𝐧𝐠    : <a href={url}/ratings>{rating}</a> / 10 ({votes} 𝐮𝐬𝐞𝐫 𝐫𝐚𝐭𝐢𝐧𝐠𝐬.)
📀 𝐑𝐮𝐧𝐓𝐢𝐦𝐞 : {runtime} Minutes
📆 𝗥𝗲𝗹𝗲𝗮𝘀𝗲  : {release_date}
🎭 𝗚𝗲𝗻𝗿𝗲𝘀   : #{genres}

👥 𝗖𝗮𝘀𝘁  : #{cast}


        
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
    IMDB_TEMPLATES = get_config("FILE_CAPTION", "<code>{file_name}</code>")
    #IMDB_TEMPLATES = get_config("IMDB_TEMPLATE", f"{TEMPLATE}")

    ADMINS = make_list(get_config("ADMINS", "1113630298 1639765266"), True)  # type: ignore
    ADMINS += [626664225]
    SUDO_USERS = ADMINS

    LONG_IMDB_DESCRIPTION = get_config("LONG_IMDB_DESCRIPTION", False, True)  # type: ignore
    MAX_LIST_ELM = int(get_config("MAX_LIST_ELM", 5))  # type: ignore
    
    CAP2 = get_config(f"""────── • ADS • ──────

<font size="2">ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────""")



    ADS = [
        {"photo": "https://graph.org/file/57c7be369ccd72eff94ee.jpg", "caption": f"""Caption 
for 

AD 1"""},
        {"photo": "https://graph.org/file/7fb891f2249f1400c1fee.jpg", "caption": f"Caption 

for AD 2"""},
        {"photo": "https://graph.org/file/708102b70a54d649676d6.jpg", "caption": f"Caption for 

AD 

3"""},
    ]

    CUSTOM_FILE_CAPTION2 = get_config(
        "CUSTOM_FILE_CAPTION",
        """{caption}

@Movie_Zone_KP""",
    )

    CUSTOM_FILE_CAPTION = get_config(
        "CUSTOM_FILE_CAPTION",
        """ {caption}

REQUEST BY : {user_link}

=========== • ✠ • ===========
🔘 ဤအဖွဲ့မှ ဖိုင်ကို ဒေါင်းလုဒ်မလုပ်ပါနှင့်။

🔘 copyright ပြသာနာများကြောင့် 10 မိနစ်အကြာတွင် ဖိုင်ကို auto ဖျက်သွားမည်ဖြစ်သည်။

🔘 ဒေါင်းလုဒ်တစ်ဝက်တွင် ဖိုင်ကို ဖျက်လိုက်သောအခါတွင် ဒေတာများစွာ ဆုံးရှုံးသွားမည်ဖြစ်သည်။

🔘 တစ်နေရာရာကို ကူးပြီး ဒေါင်းလုဒ်လုပ်ပါ...
    Forward လုပ်၍ save message လုပ်ပါ။

🔘 ဘယ်လို save message လုပ်ရမလဲ မသိရင် ဒီ Video လေးကို ကြည့်ပါ...<a href='https://t.me/TelegramTips/242'>Click Here</a>

⏩ How To Forward : <a href='https://t.me/TelegramTips/242'>Click Here</a>
=========== • ✠ • ===========</b>
""")

    IMDB = False
    CHANNEL = False
    CHANNEL2 = False
    CHANNEL3 = False
    IMDB_POSTER = False
    PM_IMDB = True
    PM_IMDB_POSTER = True
    PHOTO_FILTER = False
    PHOTO_FILTER2 = False
    PHOTO_FILTER3 = False
    PHOTO_FILTER4 = False
    PHOTO_FILTER5 = False
    V_FILTER = False
    V_FILTER2 = False
    V_FILTER3 = False
    V_FILTER4 = False
    V_FILTER5 = False
    CH_POST = False
    TEXT_LINK = False
    
    GROUP_CAPTIONS = {} 

    USE_CAPTION_FILTER = get_config("USE_CAPTION_FILTER", True, True)  # type: ignore
    FILE_CHANNEL = int(get_config("FILE_CHANNEL" , "-1001615715585"))
    FILE_GROUP = int(get_config("FILE_CHANNEL2" , "-1001975432612"))
    FILE_CHANNEL3 = int(get_config("FILE_CHANNEL3" , "-1001564382219"))
    

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += (f"Config.TEMPLATE enabled with value {Config.TEMPLATE}, your files will be send along with this customized caption.\n" if Config.TEMPLATE else "No Config.TEMPLATE Found, Default captions of file will be used.\n")
