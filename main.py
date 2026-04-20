import discord
from discord.ext import commands
from googletrans import Translator
from langdetect import detect
import asyncio
from flask import Flask
from threading import Thread

# ===== Webサーバー（Render用）=====
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ===== Bot設定 =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # 自分・bot・Webhook無視
    if message.author.bot:
        return
    if message.webhook_id is not None:
        return

    text = message.content.strip()

    # 短すぎる文章は無視
    if len(text) < 2:
        return

    # 言語判定
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

    # 翻訳
    try:
        translated = translator.translate(text, dest=target).text
    except:
        return

    # Webhook取得 or 作成
    webhooks = await message.channel.webhooks()
    webhook = None

    for wh in webhooks:
        if wh.name == "translator_bot":
            webhook = wh
            break

    if webhook is None:
        webhook = await message.channel.create_webhook(name="translator_bot")

    # 送信（ユーザー再現）
    await webhook.send(
        content=translated,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

    await bot.process_commands(message)

# ===== 起動 =====
keep_alive()
bot.run("TOKEN")
