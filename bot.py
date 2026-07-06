import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")

def get_btc():
    r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    return r.json()["bitcoin"]["usd"]

def clean_number(num):
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    s = str(num)
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s

async def start(update, context):
    await update.message.reply_text("Send me a USD amount like 500")

async def handle(update, context):
    try:
        usd = float(update.message.text)
        price = get_btc()
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
        
    except:
        pass

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
