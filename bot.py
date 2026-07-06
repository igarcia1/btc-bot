import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

async def start(update, context):
    await update.message.reply_text("Bot is working! Send me a number.")

async def handle(update, context):
    try:
        usd = float(update.message.text)
        btc = usd / 50000
        await update.message.reply_text("BTC: " + str(round(btc, 8)))
    except:
        await update.message.reply_text("Send a number please")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("Bot is running...")
app.run_polling()
