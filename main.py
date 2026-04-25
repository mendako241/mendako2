import discord
from discord.ext import commands
from googletrans import Translator
from langdetect import detect
from flask import Flask
from threading import Thread
import os

# Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Discord Bot
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

    if message.webhook_id is not None:
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

    await message.channel.send(translated)

keep_alive()
bot.run(os.getenv("TOKEN"))
