import logging
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
MODEL_USERNAME = "YourLovelyModelA"
PUBLIC_CHANNEL = "Bella_liii"
PAYPAL_LINK = "https://www.paypal.me"
PAYMENT_PLATFORM_LINK = "https://app.keepz.me/pay?qrType=DEFAULT&receiverType=USER&receiverId=2e9d8c7c-37f4-4b44-a4e2-7752e88248a1"

PRODUCTS = {
    "vip": {
        "name": "💎 VIP Subscription",
        "tariffs": {
            "1month": {"stars": 250, "usd": 7, "name": "1 month"},
            "3months": {"stars": 550, "usd": 18, "name": "3 months"},
            "lifetime": {"stars": 1000, "usd": 30, "name": "Lifetime"}
        }
    },
    "chat": {
        "name": "💬 Chat with me",
        "price": {"stars": 100, "usd": 3},
        "description": "Always stay in touch with me"
    },
    "private": {
        "name": "🔞 Private C2C",
        "price": {"stars": 1700, "usd": 50},
        "description": "Exclusive private content"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = "🌟 *Hi, I'm Bella!* 🌟\n\nChoose an option below:"
    keyboard = [
        [InlineKeyboardButton("🔍 Check subscription", callback_data="check_sub")],
        [InlineKeyboardButton(f"💌 Message @{MODEL_USERNAME}", url=f"https://t.me/{MODEL_USERNAME}")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for p_id, p_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(p_data["name"], callback_data=f"prod_{p_id}")])
    
    # Кнопка назад в самое начало
    keyboard.append([InlineKeyboardButton("🔙 Back to Start", callback_data="to_start")])
    
    await query.edit_message_text("Hi sweetie ❤️\nSelect a product:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    p_id = query.data.split('_')[1]
    p_data = PRODUCTS[p_id]
    context.user_data["current_product"] = p_id

    keyboard = []
    if "tariffs" in p_data:
        for t_id, t in p_data["tariffs"].items():
            keyboard.append([InlineKeyboardButton(f"{t['name']} - {t['stars']}⭐/{t['usd']}$", callback_data=f"tarr_{t_id}")])
        text = f"Select tariff for {p_data['name']}:"
    else:
        keyboard.append([InlineKeyboardButton(f"⭐ {p_data['price']['stars']} stars", callback_data="pay_stars_fixed")])
        keyboard.append([InlineKeyboardButton(f"💵 {p_data['price']['usd']}$ USD", callback_data="pay_usd_fixed")])
        text = f"{p_data['name']}\n\n{p_data['description']}"

    # Кнопка назад к списку продуктов
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="check_sub")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    p_id = context.user_data.get("current_product")
    p_data = PRODUCTS[p_id]
    
    keyboard = []
    if "tarr_" in data:
        t_id = data.split('_')[1]
        context.user_data["current_tariff"] = t_id
        t_data = p_data["tariffs"][t_id]
        keyboard = [
            [InlineKeyboardButton(f"⭐ {t_data['stars']} stars", callback_data="pay_stars_final")],
            [InlineKeyboardButton(f"💵 {t_data['usd']}$ USD", callback_data="pay_usd_final")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"prod_{p_id}")]
        ]
        await query.edit_message_text(f"Payment for {t_data['name']}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif "pay_stars" in data:
        price = p_data["price"]["stars"] if "fixed" in data else p_data["tariffs"][context.user_data["current_tariff"]]["stars"]
        # Здесь кнопка назад ведет на уровень выше к выбору способа оплаты
        back_call = f"prod_{p_id}" if "fixed" in data else f"tarr_{context.user_data.get('current_tariff')}"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=back_call)]]
        
        await query.edit_message_text(
            f"🎁 How to gift {price} stars:\n\n1. Visit [@{MODEL_USERNAME}](https://t.me/{MODEL_USERNAME})\n2. Send {price} stars\n3. Send screenshot here.",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif "pay_usd" in data:
        price = p_data["price"]["usd"] if "fixed" in data else p_data["tariffs"][context.user_data["current_tariff"]]["usd"]
        keyboard = [
            [InlineKeyboardButton("💳 PayPal", url=PAYPAL_LINK)],
            [InlineKeyboardButton("🏦 Platform", url=PAYMENT_PLATFORM_LINK)],
            [InlineKeyboardButton("🔙 Back", callback_data=f"prod_{p_id}")]
        ]
        await query.edit_message_text(f"Pay ${price} via links below:", reply_markup=InlineKeyboardMarkup(keyboard))

async def to_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    welcome_text = "🌟 *Hi, I'm Bella!* 🌟\n\nChoose an option below:"
    keyboard = [
        [InlineKeyboardButton("🔍 Check subscription", callback_data="check_sub")],
        [InlineKeyboardButton(f"💌 Message @{MODEL_USERNAME}", url=f"https://t.me/{MODEL_USERNAME}")]
    ]
    await query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(to_start_callback, pattern="^to_start$"))
    app.add_handler(CallbackQueryHandler(show_products_menu, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(show_options, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(handle_payment, pattern="^(tarr_|pay_)"))
    app.run_polling()

if __name__ == '__main__':
    main()