from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from telegram.error import TelegramError
from sniper_runner import start_sniping_for_user, stop_sniping_for_user
from session_manager import UserSession
from config import CONFIG
import base58

custom_keyboard = [["/setwallet", "/setamount"], ["/snipeon", "/snipeoff"], ["/status"]]
reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

user_sessions = {}
WELCOME_TEXT = """
Welcome to *Solsnipery* — your memecoin auto-sniper on Solana!

• /setwallet - Set Phantom private key
• /setamount - Amount per trade (e.g. 0.01)
• /snipeon - Start watching wallets
• /snipeoff - Stop sniper
• /status - View current settings
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup, parse_mode="Markdown")

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your **burner private key** (Phantom) now.", parse_mode="Markdown")

def is_valid_base58_key(msg):
    try:
        decoded = base58.b58decode(msg)
        return len(decoded) in [32, 64]
    except Exception:
        return False

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.chat_id
    msg = update.message.text.strip()
    if uid not in user_sessions:
        user_sessions[uid] = UserSession()

    if len(msg.split()) in [12, 24]:
        user_sessions[uid].private_key = msg
        await update.message.reply_text("✅ Mnemonic saved.")
    elif is_valid_base58_key(msg):
        user_sessions[uid].private_key = msg
        await update.message.reply_text("✅ Base58 private key saved.")
    else:
        try:
            amount = float(msg)
            user_sessions[uid].sol_amount = amount
            await update.message.reply_text(f"✅ Amount set: {amount} SOL per trade.")
        except:
            await update.message.reply_text("⚠️ Invalid input.")

async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send amount per trade (e.g., 0.01):")

async def snipe_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.chat_id
    session = user_sessions[uid]
    start_sniping_for_user(uid, session)
    await update.message.reply_text("🚀 Sniping started... Monitoring wallets.")

async def snipe_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stop_sniping_for_user(update.message.chat_id)
    await update.message.reply_text("🛑 Sniping paused.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = user_sessions.get(update.message.chat_id)
    if session:
        await update.message.reply_text(
            f"📊 Wallet: [hidden]\n💰 Amount: {session.sol_amount} SOL\n🧠 Status: {'ON' if session.sniping else 'OFF'}"
        )
    else:
        await update.message.reply_text("⚠️ No session found.")

def start_bot():
    app = ApplicationBuilder().token(CONFIG["telegram_token"]).build()

    async def error_handler(update, context):
        print(f"Error while handling update: {context.error}")

    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setwallet", set_wallet))
    app.add_handler(CommandHandler("setamount", set_amount))
    app.add_handler(CommandHandler("snipeon", snipe_on))
    app.add_handler(CommandHandler("snipeoff", snipe_off))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()
