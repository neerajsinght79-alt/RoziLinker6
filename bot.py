import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *

bot = Client("rozi",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=TOKEN)

users_dict = {}

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if user_id in users_dict:
        movie_info = users_dict.pop(user_id)
        await message.reply_document(
            document=movie_info["file_id"],
            caption=f"🎬 {movie_info['title']}",
        )
    else:
        await message.reply_text("👋 Welcome to Rozi Movie Bot!\nSearch movies in our group to get started.")

@bot.on_message(filters.group & filters.text & ~filters.edited)
async def group_search(client, message):
    if message.chat.id != GROUP_ID:
        return
    if len(message.text) < 3:
        return
    async for msg in bot.search_messages(SOURCE_BOT, query=message.text, limit=5):
        if msg.document:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Get Link", callback_data=f"get_{msg.document.file_id}_{msg.caption}")]
            ])
            await message.reply(
                text=f"🎬 {msg.caption}",
                reply_markup=btn
            )

@bot.on_callback_query(filters.regex(r"get_(.+?)_(.+)"))
async def handle_get_link(client, callback_query):
    file_id, caption = callback_query.data.split("_", 1)
    user_id = callback_query.from_user.id

    short_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url=https://t.me/{BOT_USERNAME[1:]}?start=verify{user_id}"
    users_dict[user_id] = {"file_id": file_id, "title": caption}

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify via Link", url=short_url)]
    ])
    await callback_query.message.reply("🔐 Please verify via link below to get your movie:", reply_markup=button)
    await callback_query.answer("Check your DM with Rozi Bot!")

bot.run()
