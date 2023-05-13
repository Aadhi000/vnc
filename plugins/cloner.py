import re

import logging

from pymongo import MongoClient

from pyrogram import Client, filters

from pyrogram.types import Message

from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid

from info import API_ID, API_HASH, ADMINS, CLONE_SESSIONS, CLONED_SESSIONS

from info import DATABASE_URI as MONGO_URL

logging.basicConfig(

    level=logging.ERROR,

    format="%(asctime)s - %(levelname)s - %(message)s",

    handlers=[

        logging.FileHandler("error.log"),

        logging.StreamHandler()

    ]

)

mongo_client = MongoClient(MONGO_URL)

mongo_db = mongo_client["cloned_bots"]

@Client.on_message((filters.regex(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}')) & filters.private)

async def on_clone(self, message):

    try:

        user_id = message.from_user.id

        user_name = message.from_user.first_name

        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', message.text, re.IGNORECASE)

        bot_token = bot_token[0] if bot_token else None

        bot_id = re.findall(r'\d[0-9]{8,10}', message.text)

        if not str(message.forward_from.id) != "93372553":

            msg = await message.reply_text(f"ʙᴏᴛ ᴛᴏᴋᴇɴ ›› <code>{bot_token}</code>\n\nᴄʟᴏᴀɴɪɴɢ ʙᴏᴛ")

            try:

                ai = Client(

                    f"{bot_token}", API_ID, API_HASH,

                    bot_token=bot_token,

                    plugins={"root": "plugins"},

                )

                await ai.start()

                bot = await ai.get_me()

                details = {

                    'bot_id': bot.id,

                    'is_bot': True,

                    'user_id': user_id,

                    'name': bot.first_name,

                    'token': bot_token,

                    'username': bot.username

                }

                mongo_db.bots.insert_one(details)

                await msg.edit_text(f<b>"› 📍 ʏᴏᴜʀ ʙᴏᴛ @{bot.username} ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ᴡᴏʀᴋɪɴɢ ᴘᴇʀғᴇᴄᴛʟʏ ғᴏʀ ᴛʜɪs ʟɪᴋᴇ ᴄʟᴏɴᴇ ғᴇᴀʀᴜʀᴇ ʙᴏᴛs ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ @aboutaadhi ‹</b>\n\n<i>✅ ᴄʀᴇᴅɪᴛs : @aboutaadhi</i>")

            except BaseException as e:

                logging.exception("🚫 ᴄʟᴏɴɪɴɢ ᴇɴᴅs ᴡɪᴛʜ ᴇʀʀʀᴏ 🚫")

                await msg.edit_text(f"<b>› ʙᴏᴛ ᴛᴏᴋᴇɴ ᴍᴀʏʙᴇ ᴇxᴘɪʀᴇᴅ..!\n› ᴄʀᴇᴀᴛᴇ ɴᴇᴡ ᴀɴᴅ sᴇɴᴅ ʜᴇʀᴇ</b>")

    except Exception as e:

        logging.exception("Error while handling message.")

@Client.on_message(filters.command("clonedbots") & filters.private)

async def cloned_bots_list(client, message):

    try:

        user_id = message.from_user.id

        user_name = message.from_user.first_name

        bots = list(mongo_db.bots.find({'user_id': user_id}))

        if len(bots) == 0:

            await message.reply_text("You haven't cloned any bots yet.")

            return

        text = "<b>Your cloned bots:</b>\n\n"

        for bot in bots:

            text += f"- @{bot['username']} ({bot['name']})\n"

            text += f"  Bot ID: {bot['bot_id']}\n"

            text += f"  Token: {bot['token']}\n"

            text += "\n"

        await message.reply_text(text)

    except Exception as e:

        logging.exception("Error while handling clonedbots command.")

@Client.on_message(filters.command('cloned_count') & filters.private)

async def cloned_count(client, message):

    user_id = message.from_user.id

    if user_id not in ADMINS:

        await message.reply_text("You are not authorized to use this command.")

        return

    cloned_bots = mongo_db.bots.find()

    count = cloned_bots.count()

    if count == 0:

        await message.reply_text("No bots have been cloned yet.")

    else:

        bot_usernames = [f"@{bot['username']}" for bot in cloned_bots]

        bot_usernames_text = '\n'.join(bot_usernames)

        await message.reply_text(f"{count} bots have been cloned:\n\n{bot_usernames_text}")
        
        @Client.on_message(filters.command(["removebot"]) & filters.user(ADMINS))

async def remove_bot(Client: message):

    bot_username = message.text.split(" ", maxsplit=1)[1].strip()

    bot_data = mongo_db.bots.find_one_and_delete({"username": bot_username})

    if bot_data:

        bot_id = bot_data["bot_id"]

        cloned_sessions = mongo_db.cloned_sessions.find({"bot_id": bot_id})

        if cloned_sessions.count() > 0:

            for session in cloned_sessions:

                await session.stop()

                mongo_db.cloned_sessions.delete_one({"_id": session["_id"]})

        await message.reply_text(f"Bot @{bot_username} removed successfully.")

    else:

        await message.reply_text(f"Bot @{bot_username} is not in the cloned bots list.")

@Client.on_message(filters.command("deletecloned") & filters.private)

async def delete_cloned_bot(client, message):

    try:

        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', message.text, re.IGNORECASE)

        bot_token = bot_token[0] if bot_token else None

        bot_id = re.findall(r'\d[0-9]{8,10}', message.text)

        cloned_bot = mongo_collection.find_one({"token": bot_token})

        if cloned_bot:

            mongo_collection.delete_one({"token": bot_token})

            await message.reply_text("The cloned bot has been removed from the list and its details have been removed from the database.")

        else:

            await message.reply_text("The bot token provided is not in the cloned list.")

    except Exception as e:

        logging.exception("Error while deleting cloned bot.")

        await message.reply_text("An error occurred while deleting the cloned bot.")
