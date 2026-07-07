import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

async def start(update: Update, context):
    await update.message.reply_text("Send me a number")

async def handle(update: Update, context):
    try:
        num = float(update.message.text)
        await update.message.reply_text("You sent: " + str(num))
    except:
        await update.message.reply_text("Send a number")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("Bot running...")
app.run_polling()
