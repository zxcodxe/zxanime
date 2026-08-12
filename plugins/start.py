from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import humanize
import asyncio
from datetime import timedelta # <--- IMPORT THIS

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await client.mongodb.present_user(user_id):
        await client.mongodb.add_user(user_id)
    if await client.mongodb.is_banned(user_id):
        return await message.reply("**You have been banned!**")

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        string = await decode(base64_string)
        argument = string.split("-")
        
        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db))
                end = int(int(argument[2]) / abs(client.db))
                ids = range(start, end + 1)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Error decoding range link: {e}")
                return

        elif len(argument) == 2:
            try:
                payload = argument[1]
                if payload.startswith("batch_"):
                    batch_key = payload.split("_", 1)[1]
                    ids = await client.mongodb.get_batch(batch_key)
                    if not ids:
                        return await message.reply("This link may have expired or is invalid.")
                else:
                    ids = [int(int(payload) / abs(client.db_channel.id))]
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Error decoding link: {e}")
                return
        
        if not ids:
            return await message.reply("Invalid link format or expired link.")

        temp_msg = await message.reply("ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...")
        
        messages_to_send = []
        try:
            messages_to_send = await get_messages(client, ids)
        except Exception as e:
            await temp_msg.edit_text("Something went wrong.")
            client.LOGGER(__name__, client.name).warning(f"Error getting messages: {e}")
            return
        
        if not messages_to_send:
            return await temp_msg.edit("Couldn't find the files.")
        
        await temp_msg.delete()

        yugen_msgs = []
        for msg in messages_to_send:
            caption = msg.caption.html if msg.caption else ""
            reply_markup = msg.reply_markup if not client.disable_btn else None
            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=client.protect,
                    parse_mode=ParseMode.HTML
                )
                yugen_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=client.protect,
                    parse_mode=ParseMode.HTML
                )
                yugen_msgs.append(copied_msg)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to send message: {e}")
                
        if yugen_msgs and client.auto_del > 0:
            delete_time = humanize.naturaldelta(timedelta(seconds=client.auto_del))
            
            k = await client.send_message(
                chat_id=message.from_user.id, 
                text=f'<b>⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....\n<blockquote>ᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {delete_time}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.</blockquote>\n<blockquote>ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ɢᴏᴏᴅ ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ᴀᴘᴘ ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ!</blockquote></b>',
                parse_mode=ParseMode.HTML
            )
            asyncio.create_task(delete_files(yugen_msgs, client, k, text))
    else:
        buttons = [[InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="about"), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])
        
        photo = client.messages.get("START_PHOTO", "")
        start_text = client.messages.get('START', 'No Start Message').format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f'@{message.from_user.username}' if message.from_user.username else 'None',
            mention=message.from_user.mention,
            id=message.from_user.id
        )

        if photo:
            await message.reply_photo(photo, caption=start_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        else:
            await message.reply_text(start_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
