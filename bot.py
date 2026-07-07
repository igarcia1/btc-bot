import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

def start(update, context):
    update.message.reply_text("Bot is working! Send me a number.")

def handle(update, context):
    try:
        usd = float(update.message.text)
        btc = usd / 50000
        update.message.reply_text("BTC: " + str(round(btc, 8)))
    except:
        update.message.reply_text("Send a number please")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
print("Bot is running...")
updater.start_polling()
updater.idle()
