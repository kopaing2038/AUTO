import re
from os import environ



class script(object):
  
  START_TEXT = """Hello {mention} 👋


Click your correct language button Bro😌
"""

  MM_START_TEXT = """ဟေ့ {mention} 👋

ကျွန်ုပ်သည် စွမ်းရည်များစွာရှိသော အဆင့်မြင့် Auto filter bot တစ်ခုဖြစ်သည်။ 

ကျွန်ုပ်၏ အလိုအလျောက် စစ်ထုတ်မှုတွင် အကန့်အသတ်မရှိပါ။ 

- - - - - - - - - - - - - - - 
သင်၏ bot များကို တည်းဖြတ်ရန်အတွက် 
ဆက်သွယ်ရန် :- @KOPAINGLAY15
- - - - - - - - - - - - - - -"""

  ENG_START_TEXT = """Hey {mention} 👋

I am an advanced Auto filter bot with many capabilities.

My Auto filter has no limits. 

- - - - - - - - - - - - - - -
For your bot editing
Contact :- @KOPAINGLAY15
- - - - - - - - - - - - - - -"""

  KOREAN_START_TEXT = """안녕하세요 {mention} 👋

저는 다양한 기능을 갖춘 고급 자동 필터 봇입니다.

내 자동 필터에는 제한이 없습니다.

- - - - - - - - - - - - - - -
봇 편집용
연락처 :- @KOPAINGLAY15
- - - - - - - - - - - - - - -"""

  THAI_START_TEXT = """สวัสดี {mention}👋

ฉันเป็นบอทตัวกรองอัตโนมัติขั้นสูงที่มีความสามารถมากมาย

ตัวกรองอัตโนมัติของฉันไม่มีขีดจำกัด

- - - - - - - - - - - - - - -
สำหรับการแก้ไขบอทของคุณ
ติดต่อ :- @KOPAINGLAY15
- - - - - - - - - - - - - - -"""

  CHN_START_TEXT = """嘿 {mention}👋

我是一个具有多种功能的高级自动过滤机器人。

我的自动过滤器没有限制。

- - - - - - - - - - - - - - -
用于您的机器人编辑
联系方式：-@KOPAINGLAY15
- - - - - - - - - - - - - - -"""
  
  JAPAN_START_TEXT = """こんにちは、{mention} 👋

私は多くの機能を備えた高度な自動フィルター ボットです。

私の自動フィルターには制限がありません。

- - - - - - - - - - - - - - -
ボット編集用
連絡先:- @KOPAINGLAY15
- - - - - - - - - - - - - - -"""

  HELP_TEXT = """<b>ɴᴏᴛᴇ:</b>
  
<code>Tʜɪs Mᴏᴅᴜʟᴇ Oɴʟʏ Wᴏʀᴋs Fᴏʀ User</code>

🔋 <u><b>Basic Command</b></u>
• 
• /stats - <code>ᴛᴏ ɢᴇᴛ ꜱᴛᴀᴛᴜꜱ ᴏꜰ ꜰɪʟᴇꜱ ɪɴ ᴅʙ.</code>
• /song -  mp3 & mp4 music download 
• /id 
• /info 
• /imdb 
• /react
• /hide 
• /show
• /joke
• /animalfact 
• /dogfact 
• /catfact
• /gban 
• /tm
• /tx
•
•
"""
  
  FATURES =  START_TEXT

  THANK_TXT = """ᴛʜᴀɴᴋ ᴜ ꜰᴏʀ ᴄʜᴇᴄᴋ ᴍy ᴅᴀᴛᴀꜱ ᴀɴᴅ ꜱᴛᴀʀᴛɪɴɢ ᴍᴇ
ᴀᴅᴅ ᴍᴇᴛ ᴏ ᴜʀ ɢʀᴏᴜᴩ ᴀɴᴅ ᴇɴᴊᴏy 💝"""



  VIP_LINK = "https://t.me/Kpautoreply_bot"
  
  BOT_USE_LINK = "https://t.me/KP_User_Guide"
  
  DONATE_LINK = "https://t.me/kpmovielist/277"

  SUPPORT_GP_LINK = "https://t.me/+z5lhEpxP5Go4MWM1"
  
  UPDATE_CH_LINK = "https://t.me/MKSVIPLINK2"
  
  ALL_CH_LINK = "https://t.me/Movie_Zone_KP/3"
  
  GP1_LINK = "https://t.me/MKS_REQUESTGROUP"


  
  E_SERIES_LINK = 'https://t.me/Serieslists'
  
  CHINESE_LINK = 'https://t.me/Chinese_Series_MCS'
  
  THAI_LINK = 'https://t.me/ThaiSeries_MTS'
  
  BOLLYWOOD_LINK = 'https://t.me/+1-VidI6DzaA0MDA1'
  
  ANIME_LINK = 'https://t.me/Anime_Animation_Series'
  
  K_SERIES_LINK = 'https://t.me/MKSVIPLINK'  



  OWNER_LINK = 'https://t.me/KOPAINGLAY15'
  
  M_LINK = 'https://t.me/KOPAINGLAY15'
  
  SOURCE_CODE = OWNER_LINK
  
  CHNL_LNK = "https://t.me/kpmovielist"
  
  GRP_LNK =  "https://t.me/MKS_REQUESTGROUP"

  ALL_CHANNEL = """ALL MOVIE LIST
    
🌟 MOVIE ZONE 🌟    
https://t.me/Movie_Zone_KP

🌟KP World Movie 1 🌟
https://t.me/+rYX-JDbH9MoxMDBl

🌟KP World Movie 2 🌟
https://t.me/joinchat/ISraAtYHjKQ4ODU1

🌟KP World Movie 3 🌟
https://t.me/joinchat/kWUmZootKSxhMDll

🌟KP World Movie 4 🌟
https://t.me/joinchat/5j1Z-515I_k2YWM1

🌟KP World Movie 5 🌟
https://t.me/+bB-NEPWIB5VhM2E1

🌟Kp Cartoon Movie 🌟
https://t.me/joinchat/WcNZvMdzkzc2NThl

🌟 Movie By Artist Name 🌟
https://t.me/+me4-0JmJkIplOGY1

🔞KP Adult Channel🔞
https://t.me/+UuQm91WPBbU2NzA1

====================

Korean Series များကြည့်ရန်

🌟MKS Main Channel🌟
https://t.me/mksviplink

🌟MKS Main Channel🌟
https://t.me/mksviplink2

🌟MKS All Drama Team 🌟
https://t.me/joinchat/3xS_MTfvJSEzZjY1

🌟MKS Ongoing Channel 🌟
https://t.me/ONGOING_MKS

====================

🌟KP World Movie List 🌟
https://t.me/kpmovielist

- OWNER : - <a href=https://t.me/KOPAINGLAY15>Mr.PAING LAY</a>**"""
  

  ALL_GROUPS = """ALL GROUP LIST
    
🌟 မြန်မာစာတန်းထိုးရုပ်ရှင် 🌟
 https://t.me/Movie_Group_MMSUB
 
🌟KP Movie Request Group 🌟
https://t.me/joinchat/_1Hs8V60HGs1NzA1

🌟 Movie Zone  🌟
https://t.me/+e0fXraY_I743Mjk9

🌟 Movie Zone BACKUP 🌟
https://t.me/+e0fXraY_I743Mjk9

=================

🌟 Request Group 🌟 
https://t.me/MKS_RequestGroup

🌟 Request Group 2 🌟 
https://t.me/+z5lhEpxP5Go4MWM1

- OWNER : - <a href=https://t.me/KOPAINGLAY15>Mr.PAING LAY</a>**""" 
  
  
    
  VIP_TEXT  =  """VIP Series Info
    
Hello
 1. For the English Series, Lifetime will have to pay 3000 Kyats.
English Series List
https://t.me/Serieslists

 2. For the Thailand Series, Lifetime should pay only 3000 Kyats.
Thailand Series List
https://t.me/ThaiSeries_MTS

 3. For the Chinese Series, Lifetime should pay only 3000 Kyats.
Chinese Series List
https://t.me/Chinese_Series_MCS

 ⭐️ If you join the Package Membership for all 3 Series Channels, you will only pay 8000 Kyats from Lifetime.  (The population is limited.)
 
Take a screenshot of this Acc and send it. 
👉🏻 @KPOWNER"""
  
  
   
  DONATE = """Donate ♦️ 

Wave 
Acc Phone No -09404840521

KBZ Pay 
Acc Phone No -09404840521

AYA Pay 
Acc Phone No -09404840521


အကြံပေးချက်များနဲ့ အဆင်မပြေမူများရှိပါက  👉 @KPOWNERBOT"""
    
  DEVS_TEXT = """DEVS
    
✯ Modified By @KOPAINGLAY15 🙂
    
For your bot editing
Contact :- @KOPAINGLAY15

✯ Special Courtesy To :
   ● Team Eva Maria
   ● Team TrojanzHex
   ● Team CrazyBotsz
   ● Team InFoTel 
   ● 
   
✯ Bot Managed By :
   ● @KOPAINGLAY15
   ● @PAINGLAY15
   ●               
 """
  OWNER_TXT = """<b>OWNER:</b>
    
- OWNER 1 : - <a href=https://t.me/KPOWNER>Mr.SITT</a>
- OWNER 2 : - <a href=https://t.me/KOPAINGLAY15>Mr.PAING LAY</a>**
- OWNER 3 : - <a href=https://t.me/MKSVIPLINK>MKS</a>**"""

  ABOUT_TXT = """✯ 𝙼𝚈 𝙽𝙰𝙼𝙴 : AUTO FILTER BOT
  
✯ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁 : - <a href=https://t.me/KOPAINGLAY15>Mr.PAING LAY</a>**

✯ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈 : 𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼
✯ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴 : 𝙿𝚈𝚃𝙷𝙾𝙽 𝟹
✯ 𝙳𝙰𝚃𝙰 𝙱𝙰𝚂𝙴 : 𝙼𝙾𝙽𝙶𝙾-𝙳𝙱
 
✯ Modified By @KOPAINGLAY15 🙂
    
✯ Special Courtesy To :
   ● SUBINP
      
✯ Bot Managed By :
   ● @KOPAINGLAY15
   ● @PAINGLAY15
          
 
သင်၏ Auto bot တည်းဖြတ်မှုအတွက်
ဆက်သွယ်ရန်- @KOPAINGLAY15

   """

  ADMINONLY_TXT = """
• /status - <code>ᴛᴏ ɢᴇᴛ sᴛᴀᴛᴜs ᴏғ sᴇʀᴠᴇʀ</code>
• /stats - <code>ᴛᴏ ɢᴇᴛ ᴅᴀᴛᴀᴛʙᴀꜱᴇ ꜱᴛᴀᴛᴜꜱ</code>
• /del - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ.</code>
• /delete - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ.</code>
• /delete1 - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ 1.</code>
• /delete2 - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ 2.</code>
• /delete3 - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ 3.</code>
• /deleteall - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ꜰɪʟᴇs ꜰʀᴏᴍ ᴅʙ.</code>
• /broadcast - ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ</code>
• /restart - Tᴏ Rᴇsᴛᴀʀᴛ ᴀ Bᴏᴛ
• /set_sub_channel - CHANNEL ID
• /set_file_caption -  {caption} text
• /set_template - set imdb template 
• /set_admins_plus - ADMIN ID
• /show_admins_plus - ADMIN ID
• /remove_admins_plus - ADMIN ID
• /set_ads - url link
• /show_ads - 
• /set_start -   {mention} text
• /set_cap2 - caption cap2 text
• /set_pics - pic url link
• /set_pics_plus - pic url link

"""


Script = script()
