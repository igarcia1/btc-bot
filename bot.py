import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

user_selections = {}

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
        
        user_id = update.effective_user.id
        user_selections[user_id] = {
            "usd": clean_number(round(usd, 2)),
            "btc": btc_str,
            "methods": []
        }
        
        keyboard = [
            [
                InlineKeyboardButton("💳 Zelle", callback_data="toggle_zelle"),
                InlineKeyboardButton("💵 Cash App", callback_data="toggle_cashapp")
            ],
            [
                InlineKeyboardButton("📱 Apple Pay", callback_data="toggle_applepay"),
                InlineKeyboardButton("💳 Card", callback_data="toggle_card")
            ],
            [
                InlineKeyboardButton("🔄 Other", callback_data="toggle_other")
            ],
            [
                InlineKeyboardButton("✅ OK - Confirm", callback_data="confirm")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Select your payment method(s):\n(Tap to select/unselect, then press OK)",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text("❌ Please send a number like 500")

async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith("toggle_"):
        method = data.replace("toggle_", "")
        
        if user_id not in user_selections:
            user_selections[user_id] = {"methods": []}
        
        if method in user_selections[user_id]["methods"]:
            user_selections[user_id]["methods"].remove(method)
        else:
            user_selections[user_id]["methods"].append(method)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Zelle" if "zelle" in user_selections[user_id]["methods"] else "💳 Zelle",
                    callback_data="toggle_zelle"
                ),
                InlineKeyboardButton(
                    "✅ Cash App" if "cashapp" in user_selections[user_id]["methods"] else "💵 Cash App",
                    callback_data="toggle_cashapp"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Apple Pay" if "applepay" in user_selections[user_id]["methods"] else "📱 Apple Pay",
                    callback_data="toggle_applepay"
                ),
                InlineKeyboardButton(
                    "✅ Card" if "card" in user_selections[user_id]["methods"] else "💳 Card",
                    callback_data="toggle_card"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Other" if "other" in user_selections[user_id]["methods"] else "🔄 Other",
                    callback_data="toggle_other"
                )
            ],
            [
                InlineKeyboardButton("✅ OK - Confirm", callback_data="confirm")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select your payment method(s):\n(Tap to select/unselect, then press OK)",
            reply_markup=reply_markup
        )
    
    elif data == "confirm":
        if user_id not in user_selections or not user_selections[user_id].get("methods"):
            await query.edit_message_text("⚠️ Please select at least one payment method first.")
            return
        
        selected = user_selections[user_id]
        methods = selected.get("methods", [])
        method_names = {
            "zelle": "Zelle",
            "cashapp": "Cash App",
            "applepay": "Apple Pay",
            "card": "Card Payment",
            "other": "Other"
        }
        methods_list = ", ".join([method_names.get(m, m) for m in methods])
        
        summary = "$" + selected.get("usd", "0") + " " + methods_list + " for ₿" + selected.get("btc", "0") + "\n\n"
        summary += "Address and transfer ETA coming."
        
        user_selections[user_id] = {"methods": []}
        
        await query.edit_message_text(summary)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(button_callback))
print("Bot is running...")
app.run_polling()
