import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

def get_btc():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        return r.json()["bitcoin"]["usd"]
    except:
        return None

def clean_number(num):
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    s = str(num)
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s

async def start(update: Update, context):
    await update.message.reply_text("Send me a USD amount like 500")

async def handle(update: Update, context):
    try:
        usd = float(update.message.text)
        price = get_btc()
        
        if price is None:
            await update.message.reply_text("⚠️ Could not fetch BTC price. Please try again.")
            return
            
        discount = price * 0.85
        
        if usd <= 102:
            numerator = usd + 20
            denominator = price
            btc = numerator / denominator
            
            msg = "📊 BTC SPOT PRICE: $" + clean_number(round(price, 2)) + " USD\n\n"
            msg = msg + "💰 You want: $" + clean_number(round(usd, 2)) + " USD\n"
            msg = msg + "📝 Math: (" + clean_number(round(usd, 2)) + " + 20) ÷ " + clean_number(round(denominator, 2)) + "\n"
            msg = msg + "   = " + clean_number(round(numerator, 2)) + " ÷ " + clean_number(round(denominator, 2)) + "\n\n"
            msg = msg + "Exact BTC to send:"
        else:
            numerator = usd
            denominator = discount
            btc = numerator / denominator
            
            msg = "📊 BTC SPOT PRICE: $" + clean_number(round(price, 2)) + " USD\n"
            msg = msg + "🏷️ MY RATE (15% OFF): $" + clean_number(round(discount, 2)) + " USD\n\n"
            msg = msg + "💰 You want: $" + clean_number(round(usd, 2)) + " USD\n"
            msg = msg + "📝 Math: " + clean_number(round(numerator, 2)) + " ÷ " + clean_number(round(denominator, 2)) + "\n\n"
            msg = msg + "Exact BTC to send:"
        
        await update.message.reply_text(msg)
        
        btc_str = str(round(btc, 8)).rstrip('0').rstrip('.')
        await update.message.reply_text(btc_str)
        
    except Exception as e:
        await update.message.reply_text("❌ Please send a number like 500")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("Bot is running...")
app.run_polling()
