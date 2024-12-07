

import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from plugins.database import get_file_details
from pyrogram.errors import *
from pyrogram.types import *
from utils import verify_user, check_token, check_verification, get_token, react_msg
from config import *
import re
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)

BATCH_FILES = {}
buttons = [[
                InlineKeyboardButton('Click Here To Buy Membership 🥵', url="https://t.me/premiumbuy29bot")
            ]]
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            pass
    return btn

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ0


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        await react_msg(client, message)
    except:
        pass
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if message.command[1]:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start={message.command[1]}")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on try again button. 😇</b>", reply_markup=InlineKeyboardMarkup(btn))
                return
        except Exception as e:
            print(e)
    username = (await client.get_me()).username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                InlineKeyboardButton('Click Here To Buy Membership 🥵', url="https://t.me/premiumbuy29bot")
            ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('ᴄʀᴇᴀᴛᴇ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons) 
        me2 = (await client.get_me()).mention
        await message.reply_photo(photo='https://i.ibb.co/mTTg2qS/photo-2024-08-01-22-46-08-7438924214695886852.jpg',
                                caption=script.START_TXT,
                                has_spoiler = True, 
                                reply_markup=reply_markup)
        return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        if not await db.is_user_authorized(message.from_user.id):
               await message.reply_text(text="**U Are Not My Premium Member Buddy\n\n**Please Buy Membership 👇**", 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Click Here To Buy Membership 🥵", url="https://t.me/premiumbuy29bot")]])
                                                )
               return
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
    elif data.split("-", 1)[0] == "BATCH":
        try:
            if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
                ],[
                    InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                ]]
                await message.reply_text(
                    text="<b><blockquote>buddy You are not verified !\nKindly verify to continue !</blockquote></b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            return await message.reply_text(f"**Error - {e}**")
        sts = await message.reply("**🔺 ᴡᴀɪᴛ...**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
            
        filesarr = []
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                if STREAM_MODE == True:
                    # Create the inline keyboard button with callback_data
                    user_id = message.from_user.id
                    username =  message.from_user.mention 

                    log_msg = await client.send_cached_media(
                        chat_id=LOG_CHANNEL,
                        file_id=msg.get("file_id"),
                    )
                    fileName = {quote_plus(get_name(log_msg))}
                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
 
                    await log_msg.reply_text(
                        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                        quote=True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                                                            InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]])  # web stream Link
                    )
                if not await db.is_user_authorized(message.from_user.id):
                       await message.reply_text(text="**U Are Not My Premium Member Buddy\n\n**Please Buy Membership 👇**", 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Click Here To Buy Membership 🥵", url="https://t.me/premiumbuy29bot")]])
                                                )
                       return
                if STREAM_MODE == True:
                    button = [[
                        InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                        InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)
                    ],[
                        InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup=InlineKeyboardMarkup(button)
                else:
                    reply_markup = None
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=True,
                    reply_markup=reply_markup
                )
                filesarr.append(msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(button)
                )
                filesarr.append(msg)
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        if AUTO_DELETE_MODE == True:
            k = await client.send_message(chat_id = message.from_user.id, text=script.PREMIUM_TXT)
            await asyncio.sleep(AUTO_DELETE_TIME)
            for x in filesarr:
                try:
                    await x.delete()
                except:
                    pass
            await k.edit_text("𝗔𝗴𝗿 𝗮𝗮𝗽 𝗵𝗮𝗺𝗿𝗲 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲 𝗮𝗱𝗱 𝗵𝗼𝗻𝗲 𝗰𝗵𝗮𝗵𝗮𝘁𝗲 𝗵𝗮𝗶 𝗷𝗵𝗮  𝗱𝗮𝗶𝗹𝘆 𝟭𝗸 𝘃𝗶𝗱𝗲𝗼 𝘂𝗽𝗹𝗼𝗮𝗱 𝗵𝗼𝘁𝗲 𝗵𝗮𝗶 𝘁𝗼 𝗮𝗮𝗽 𝗯𝗵o𝘂𝘁 kam 𝗽𝗿𝗶𝗰𝗲 𝗺𝗲 𝗷𝗼𝗶𝗻 𝗵𝗼 𝘀𝗸𝘁𝗲 𝗵𝗮𝗶 𝗕𝘂𝘆 𝗛𝗲𝗿𝗲 - @premiumbuy29bot")
        return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

    files_ = await get_file_details(file_id)
    if not await db.is_user_authorized(message.from_user.id):
           await message.reply_text(text="**U Are Not My Premium Member Buddy\n\n**Please Buy Membership 👇**", 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Click Here To Buy Membership 🥵", url="https://t.me/premiumbuy29bot")]])
                                                )
           return
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
            btn = [[
                InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
            ],[
                InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
            ]]
            await message.reply_text(
                text="<b><blockquote>buddy You are not verified !\nKindly verify to continue !</blockquote></b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True ,  
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = '' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            
            await msg.edit_caption(f_caption)
            if STREAM_MODE == True:
                g = await msg.reply_text(
                    text=f"",
                    quote=True,
                    protect_content=True, 
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}')
                            ]
                        ]
                    )
                )
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=script.PREMIUM_TXT)
                await asyncio.sleep(AUTO_DELETE_TIME)
                try:
                    await msg.delete()
                except:
                    pass
                await g.delete()
                await k.edit_text("𝗔𝗴𝗿 𝗮𝗮𝗽 𝗵𝗮𝗺𝗿𝗲 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲 𝗮𝗱𝗱 𝗵𝗼𝗻𝗲 𝗰𝗵𝗮𝗵𝗮𝘁𝗲 𝗵𝗮𝗶 𝗷𝗵𝗮  𝗱𝗮𝗶𝗹𝘆 𝟭𝗸 𝘃𝗶𝗱𝗲𝗼 𝘂𝗽𝗹𝗼𝗮𝗱 𝗵𝗼𝘁𝗲 𝗵𝗮𝗶 𝘁𝗼 𝗮𝗮𝗽 𝗯𝗵o𝘂𝘁 kam 𝗽𝗿𝗶𝗰𝗲 𝗺𝗲 𝗷𝗼𝗶𝗻 𝗵𝗼 𝘀𝗸𝘁𝗲 𝗵𝗮𝗶 𝗕𝘂𝘆 𝗛𝗲𝗿𝗲 - @premiumbuy29bot")
            return
        except:
            pass
        return await message.reply('No such file exist.')

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
        btn = [[
            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
        ],[
            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
        ]]
        await message.reply_text(
            text="<b><blockquote>buddy You are not verified !\nKindly verify to continue !</blockquote></b>",
            protect_content=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    if not await db.is_user_authorized(message.from_user.id):
           await message.reply_text(text="**U Are Not My Premium Member Buddy\n\n**Please Buy Membership 👇**", 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Click Here To Buy Membership 🥵", url="https://t.me/premiumbuy29bot")]])
                                                )
           return
    x = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True,
    )
    if STREAM_MODE == True:
        g = await x.reply_text(
            text=f"",
            quote=True,
            protect_content=True, 
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}')
                    ]
                ]
            )
        )
    if AUTO_DELETE_MODE == True:
        k = await client.send_message(chat_id = message.from_user.id, text=script.PREMIUM_TXT)
        await asyncio.sleep(AUTO_DELETE_TIME)
        try:
            await x.delete()
        except:
            pass
        await k.edit_text("𝗔𝗴𝗿 𝗮𝗮𝗽 𝗵𝗮𝗺𝗿𝗲 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲 𝗮𝗱𝗱 𝗵𝗼𝗻𝗲 𝗰𝗵𝗮𝗵𝗮𝘁𝗲 𝗵𝗮𝗶 𝗷𝗵𝗮  𝗱𝗮𝗶𝗹𝘆 𝟭𝗸 𝘃𝗶𝗱𝗲𝗼 𝘂𝗽𝗹𝗼𝗮𝗱 𝗵𝗼𝘁𝗲 𝗵𝗮𝗶 𝘁𝗼 𝗮𝗮𝗽 𝗯𝗵o𝘂𝘁 kam 𝗽𝗿𝗶𝗰𝗲 𝗺𝗲 𝗷𝗼𝗶𝗻 𝗵𝗼 𝘀𝗸𝘁𝗲 𝗵𝗮𝗶 𝗕𝘂𝘆 𝗛𝗲𝗿𝗲 - @premiumbuy29bot")       
        

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("<b>Shortener API updated successfully to</b> " + api)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = f"`/base_site (base_site)`\n\n<b>Current base site: None\n\n EX:</b> `/base_site shortnerdomain.com`\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if base_site == None:
            await update_user_info(user_id, {"base_site": base_site})
            return await m.reply("<b>Base Site updated successfully</b>")
            
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("<b>Base Site updated successfully</b>")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🔙 back', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "start":
        buttons = [[
                InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ"),
                InlineKeyboardButton('✨ 𝙲𝙾𝙽𝚃𝙰𝙲𝚃 ✨', url="https://t.me/Harshit_contact_bot")
            ],[
                InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about')
            ],[
                InlineKeyboardButton('ᴄʀᴇᴀᴛᴇ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')
            ],[
                InlineKeyboardButton("❗ 𝙳𝙸𝚂𝙲𝙻𝙰𝙸𝙼𝙴𝚁 ❗", url="https://graph.org/vTelegraphBot-08-03-7")
            ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "clone":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CLONE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )          

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

    elif query.data.startswith("generate_stream_link"):
        _, file_id = query.data.split(":")
        try:
            user_id = query.from_user.id
            username =  query.from_user.mention 

            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(log_msg))}
            stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

            xo = await query.message.reply_text(f'🔐')
            await asyncio.sleep(1)
            await xo.delete()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

            button = [[
                InlineKeyboardButton(" Fast Download ", url=download),  # we download Link
                InlineKeyboardButton(' Watch online ', url=stream)
            ]]
            reply_markup=InlineKeyboardMarkup(button)
            await log_msg.reply_text(
                text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                quote=True,
                protect_content=True, 
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
            button = [[
                InlineKeyboardButton(" Fast Download ", url=download),  # we download Link
                InlineKeyboardButton(' Watch online ', url=stream)
            ],[
                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
            ]]
            reply_markup=InlineKeyboardMarkup(button)
            await query.message.reply_text(
                text="•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ",
                quote=True,
                protect_content=True, 
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return

@Client.on_message(filters.command("auth") & filters.user(ADMINS))
async def authorize_user(client, message):
    try:
        user_id = int(message.command[1])
        if not await db.is_user_exist(user_id):
            await message.reply_text("User does not exist in the database.")
            return

        await db.authorize_user(user_id)
        await message.reply_text(f"✅ User with ID {user_id} has been authorized.")
    except IndexError:
        await message.reply_text("❌ Please provide a user ID.")
    except ValueError:
        await message.reply_text("❌ Invalid user ID.")


@Client.on_message(filters.command("unauth") & filters.user(ADMINS))
async def unauthorize_user(client, message):
    try:
        user_id = int(message.command[1])
        if not await db.is_user_exist(user_id):
            await message.reply_text("User does not exist in the database.")
            return

        await db.unauthorize_user(user_id)
        await message.reply_text(f"✅ User with ID {user_id} has been unauthorized.")
    except IndexError:
        await message.reply_text("❌ Please provide a user ID.")
    except ValueError:
        await message.reply_text("❌ Invalid user ID.")

@Client.on_message(filters.command("all_auth") & filters.user(ADMINS))
async def all_auth_members(client, message):
    try:
        # Fetch all authorized users
        authorized_users_cursor = db.col.find({'is_authorized': True})
        authorized_users = await authorized_users_cursor.to_list(length=100)  # Fetch up to 100 users

        # Check if any authorized users exist
        if not authorized_users:
            await message.reply_text("No authorized users found.")
            return

        # Format the list of authorized users
        message_text = "👥 **Authorized Members List:**\n\n"
        for user in authorized_users:
            auth_time = user.get('auth_timestamp', None)
            formatted_time = auth_time.strftime('%Y-%m-%d %H:%M:%S UTC') if auth_time else "Unknown"
            message_text += f"<blockquote>**ID 🪪:** `{user['id']}` | **Name 📛:** {user['name']} | **Auth Time ⌚:** {formatted_time}</blockquote>\n"

        # Send the list to the admin
        await message.reply_text(message_text)
    except Exception as e:
        await message.reply_text(f"An error occurred while fetching the authorized members list: {e}")

@Client.on_message(filters.command("id") & filters.incoming)
async def get_id(client, message):
    try:
        user_id = message.from_user.id
        user_mention = message.from_user.mention  # Get user's mention
        user_name = message.from_user.first_name  # Get user's name
        chat_id = message.chat.id

        # Build the reply message
        reply_text = (
            f"<b>👤 Name:</b> {user_name}\n"
            f"<b>🙋 Mention:</b> {user_mention}\n"
            f"<b>🆔 Your User ID:</b> <code>{user_id}</code>\n"
        )

        # Include chat ID if in a group or supergroup
        if message.chat.type in ["group", "supergroup"]:
            reply_text += f"<b>👥 Group/Chat ID:</b> <code>{chat_id}</code>"

        await message.reply_text(
            text=reply_text) 
    except Exception as e:
        print(e)
