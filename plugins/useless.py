from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT, DB_URI
from datetime import datetime
from pymongo import MongoClient
from helper_func import get_readable_time


@Bot.on_message(filters.private & filters.incoming)
async def useless(_,message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)

client = MongoClient(DB_URI)
db = client['bot_database']
fsub_collection = db['force_subscriptions']
admin_collection = db['admins']

@Bot.on_message(filters.command('addfsub') & filters.user(ADMINS))
async def add_fsub(bot: Bot, message: Message):
    try:
        _, channel_id, no = message.text.split()
        fsub_collection.update_one({}, {'$set': {f'forcesub_{no}': channel_id}}, upsert=True)
        await message.reply(f'Force subscription for {channel_id} added as number {no}.')
    except ValueError:
        await message.reply('Usage: /addfsub <channel_id> <no>')

@Bot.on_message(filters.command('removefsub') & filters.user(ADMINS))
async def remove_fsub(bot: Bot, message: Message):
    try:
        _, channel_id = message.text.split()
        fsub_collection.update_one({}, {'$unset': {channel_id: 1}})
        await message.reply(f'Removed force subscription for {channel_id}.')
    except ValueError:
        await message.reply('Usage: /removefsub <channel_id>')

@Bot.on_message(filters.command('addadmin') & filters.user(ADMINS))
async def add_admin(bot: Bot, message: Message):
    try:
        _, user_id = message.text.split()
        admin_collection.update_one({}, {'$addToSet': {'admins': int(user_id)}}, upsert=True)
        await message.reply(f'User {user_id} added as admin.')
    except ValueError:
        await message.reply('Usage: /addadmin <user_id>')

@Bot.on_message(filters.command('removeadmin') & filters.user(ADMINS))
async def remove_admin(bot: Bot, message: Message):
    try:
        _, user_id = message.text.split()
        admin_collection.update_one({}, {'$pull': {'admins': int(user_id)}})
        await message.reply(f'User {user_id} removed from admins.')
    except ValueError:
        await message.reply('Usage: /removeadmin <user_id>')

@Bot.on_message(filters.command('fsub') & filters.user(ADMINS))
async def get_fsub_list(bot: Bot, message: Message):
    fsubs = fsub_collection.find_one({})
    if fsubs:
        fsub_list = '\n'.join([f'{key}: {value}' for key, value in fsubs.items() if key.startswith('forcesub_')])
        await message.reply(f'Force Subscriptions:\n{fsub_list}')
    else:
        await message.reply('No force subscriptions found.')

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))
