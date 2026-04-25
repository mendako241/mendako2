import discord
from discord.ext import commands
from googletrans import Translator
from langdetect import detect
import os

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    text = message.content.strip()

    if len(text) < 2:
        return

    try:
        lang = detect(text)
    except:
        return

    if lang == "ja":
        target = "ko"
    elif lang == "ko":
        target = "ja"
    else:
        return

    try:
        translated = translator.translate(text, dest=target).text
    except:
        return

    webhooks = await message.channel.webhooks()
    webhook = None

    for wh in webhooks:
        if wh.name == "translator_bot":
            webhook = wh
            break

    if webhook is None:
        webhook = await message.channel.create_webhook(name="translator_bot")

    await webhook.send(
        content=translated,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
