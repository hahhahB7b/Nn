# Auto-install telebot if not present
try:
    import telebot
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
    import telebot

from telebot.types import Message
from random import randint
import requests

API_TOKEN = '7911851224:AAEH5HrcpWrDZyX6KtiQ5Lnu8CGpsF5CSXI'
bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

FEE_PERCENTAGE = 0.02  # 2% default

# Admin check
def is_user_admin(chat_id, user_id):
    url = f"https://api.telegram.org/bot{API_TOKEN}/getChatMember?chat_id={chat_id}&user_id={user_id}"
    r = requests.get(url).json()
    status = r.get("result", {}).get("status", "")
    return status in ["administrator", "creator"]

# Extract field from deal text
def extract_field(text, field_name):
    for line in text.splitlines():
        if field_name in line:
            return line.split(":", 1)[-1].strip()
    return None

# Set fee command
@bot.message_handler(commands=['setfee'])
def handle_setfee(message: Message):
    global FEE_PERCENTAGE
    if not is_user_admin(message.chat.id, message.from_user.id):
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError
        new_fee = float(parts[1])
        if not (0 <= new_fee <= 1):
            raise ValueError
        FEE_PERCENTAGE = new_fee
        percent = round(new_fee * 100, 2)
        bot.reply_to(message, f"✅ Fee percentage updated to {percent}%")
    except:
        bot.reply_to(message, "❌ Usage: /setfee 0.03 (for 3%) — must be between 0 and 1")

# /add command
@bot.message_handler(commands=['add'])
def handle_add(message: Message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Please reply to the deal form.")
        return
    if not is_user_admin(message.chat.id, message.from_user.id):
        return

    text = message.reply_to_message.text
    deal_info = extract_field(text, "DEAL INFO")
    buyer = extract_field(text, "BUYER")
    seller = extract_field(text, "SELLER")
    amount = extract_field(text, "DEAL AMMOUNT")

    if not all([deal_info, buyer, seller, amount]):
        bot.reply_to(message, "❌ Invalid form. Check fields: DEAL INFO, BUYER, SELLER, DEAL AMMOUNT")
        return

    trade_id = f"TXN_{randint(10000000, 99999999):X}"
    escrower = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    response = f"""<b>Payment Received 📩</b>

🆔 <b>Trade ID</b> : <code>{trade_id}</code>
💰 <b>Amount</b> : {amount}
👤 <b>Buyer</b> : {buyer}
👤 <b>Seller</b> : {seller}
📝 <b>DEAL INFO</b> : {deal_info}

<b>Escrow by</b> {escrower}
"""

    bot.reply_to(message.reply_to_message, response)

# /done command
@bot.message_handler(commands=['done'])
def handle_done(message: Message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Please reply to the deal form.")
        return
    if not is_user_admin(message.chat.id, message.from_user.id):
        return

    text = message.reply_to_message.text
    deal_info = extract_field(text, "DEAL INFO")
    buyer = extract_field(text, "BUYER")
    seller = extract_field(text, "SELLER")
    amount = extract_field(text, "DEAL AMMOUNT")

    if not all([deal_info, buyer, seller, amount]):
        bot.reply_to(message, "❌ Invalid form. Check fields: DEAL INFO, BUYER, SELLER, DEAL AMMOUNT")
        return

    try:
        amount_value = float(''.join(c for c in amount if c.isdigit() or c == '.'))
        fee = round(amount_value * FEE_PERCENTAGE, 2)
        realized = round(amount_value - fee, 2)
    except:
        bot.reply_to(message, "❌ Couldn't parse amount.")
        return

    trade_id = f"TID{randint(100000, 999999)}"
    escrower = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    response = f"""♻️ <b>Deal Completed</b>

📤 <b>Trade ID</b> : #{trade_id}
✔️ <b>Released Amount</b> : {realized}
👤 <b>Buyer</b> : {buyer}
👤 <b>Seller</b> : {seller}

<b>Pw By</b> @team7escrow
<b>Escrower ~</b> {escrower}
"""

    bot.reply_to(message.reply_to_message, response)

print("🤖 Escrow Bot running...")
bot.infinity_polling()
