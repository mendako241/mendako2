import discord
from discord.ext import commands
from googletrans import Translator
from langdetect import detect
from flask import Flask
from threading import Thread
import os

# =========================
# Flask (Render用)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Translator Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()


# =========================
# Discord Bot設定
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()


# =========================
# 起動確認
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# =========================
# 自動翻訳
# =========================
@bot.event
async def on_message(message):

    # Bot / Webhook 無視
    if message.author.bot:
        return

    if message.webhook_id is not None:
        return

    text = message.content.strip()

    # 空文字・短文スキップ
    if len(text) < 2:
        return

    # 言語判定
    try:
        lang = detect(text)
    except:
        return

    # 日本語→韓国語 / 韓国語→日本語
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

    # Webhook取得
    webhooks = await message.channel.webhooks()

    webhook = None
    for wh in webhooks:
        if wh.name == "translator_bot":
            webhook = wh
            break

    # 無ければ作成
    if webhook is None:
        webhook = await message.channel.create_webhook(name="translator_bot")

    # ユーザー名・アイコン再現送信
    await webhook.send(
        content=translated,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

    await bot.process_commands(message)


# =========================
# 起動
# =========================
keep_alive()
bot.run(os.getenv("TOKEN"))
