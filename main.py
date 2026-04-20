import discord
from discord.ext import commands
from googletrans import Translator
from langdetect import detect

# ===== Bot設定 =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

TOKEN = "ここにトークンを貼る"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):

    # bot・webhook無視
    if message.author.bot:
        return
    if message.webhook_id is not None:
        return

    text = message.content.strip()

    # 短文スキップ
    if len(text) < 2:
        return

    # 言語判定
    try:
        lang = detect(text)
    except:
        return

    # 日本語 → 韓国語 / 韓国語 → 日本語のみ
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

    # 送信（アイコン再現）
    await webhook.send(
        content=translated,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

    await bot.process_commands(message)


# ===== 起動 =====
bot.run(TOKEN)
