import logging
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
PUBLIC_CHANNEL = "Bella_liii"
PRIVATE_CHANNEL_LINK = "https://t.me/+sbgTGMOS93o4YmNi"
PAYPAL_LINK = "https://www.paypal.me"
PAYMENT_PLATFORM_LINK = "https://app.keepz.me/pay?qrType=DEFAULT&receiverType=USER&receiverId=2e9d8c7c-37f4-4b44-a4e2-7752e88248a1"
QR_CODE_IMAGE = "https://i.ibb.co/TxZSnnLz/image.png"
MODEL_USERNAME = "YourLovelyModelA"  # Обновленный юзернейм

# Продукты и тарифы (только на английском)
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

# Тексты (только на английском)
TEXTS = {
    "welcome": "Hi sweetie ❤️\nHere are my exclusive offers for you:",
    "select_tariff": "Select tariff for {product_name}:",
    "select_payment": "Select payment method for {product_name}:\nPrice: {price}",
    "pay_stars": "⭐ {price} stars",
    "pay_usd": "💵 {price}$ (PayPal/Platform)",
    "stars_instructions": "🎁 How to gift {price} stars for '{product_name}':\n\n1. Visit my profile [@{username}](https://t.me/{username})\n2. Tap 'Gift Stars'\n3. Select {price} stars\n4. Send screenshot\n\nAfter verification you'll get access!",
    "payment_platform_instructions": "🏦 *Payment via Platform*\n\n💳 *Available methods:*\n• Bank Payment\n• Crypto Payment\n\n📱 *QR code for payment:*\n\n🔗 *Or follow the link:* [Click here]({link})\n\n⚠️ After payment send confirmation screenshot",
    "paypal_instructions": "💳 Pay {price}$ for '{product_name}' via [PayPal]({link}) and send screenshot",
    "back": "🔙 Back",
    "checking": "🔍 Checking your subscription...",
    "not_subscribed": "❌ You're not subscribed to @{channel}",
    "error": "⚠️ An error occurred. Please try again later."
}

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(chat_id=f"@{PUBLIC_CHANNEL}", user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Check sub error: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_photo = "https://i.ibb.co/m5mJxTLS/IMG-5752.jpg"
    welcome_text = (
        "🌟 *Hi, I'm Bella!* 🌟\n\n"
        "So happy to meet you! 💖\n"
        "In my bot you'll find exclusive content and special offers.\n\n"
        "Feel free to DM me anytime! 😊"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔍 Check subscription", callback_data="check_sub")],
        [InlineKeyboardButton(f"💌 Message @{MODEL_USERNAME}", url=f"https://t.me/{MODEL_USERNAME}")]
    ]
    
    await update.message.reply_photo(
        photo=welcome_photo,
        caption=welcome_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    checking_msg = await query.message.reply_text(TEXTS["checking"])
    is_member = await is_user_member(query.from_user.id, context)
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=checking_msg.message_id)

    if is_member:
        await show_products_menu(query, context)
    else:
        keyboard = [
            [InlineKeyboardButton("✅ I subscribed", callback_data="check_sub")],
            [InlineKeyboardButton("📢 Go to channel", url=f"https://t.me/{PUBLIC_CHANNEL}")]
        ]
        await query.message.reply_text(
            TEXTS["not_subscribed"].format(channel=PUBLIC_CHANNEL),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_products_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for p_id, p_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(p_data["name"], callback_data=f"prod_{p_id}")])
    
    await query.message.reply_text(TEXTS["welcome"], reply_markup=InlineKeyboardMarkup(keyboard))

async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    p_id = query.data.split('_')[1]
    p_data = PRODUCTS[p_id]
    context.user_data["current_product"] = p_id

    if "tariffs" in p_data:
        keyboard = [[InlineKeyboardButton(f"{t['name']} - {t['stars']}⭐/{t['usd']}$", callback_data=f"tarr_{t_id}")] 
                    for t_id, t in p_data["tariffs"].items()]
        keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="back_to_prods")])
        await query.edit_message_text(TEXTS["select_tariff"].format(product_name=p_data["name"]), 
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [
            [InlineKeyboardButton(TEXTS["pay_stars"].format(price=p_data["price"]["stars"]), callback_data="pay_stars_fixed")],
            [InlineKeyboardButton(TEXTS["pay_usd"].format(price=p_data["price"]["usd"]), callback_data="pay_usd_fixed")],
            [InlineKeyboardButton(TEXTS["back"], callback_data="back_to_prods")]
        ]
        await query.edit_message_text(f"{p_data['name']}\n\n{p_data['description']}", 
                                      reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    p_id = context.user_data.get("current_product")
    p_data = PRODUCTS[p_id]
    
    # Логика определения цены (тариф или фиксированная)
    if "tarr_" in data:
        t_id = data.split('_')[1]
        context.user_data["current_tariff"] = t_id
        t_data = p_data["tariffs"][t_id]
        price_stars, price_usd = t_data["stars"], t_data["usd"]
        
        keyboard = [
            [InlineKeyboardButton(TEXTS["pay_stars"].format(price=price_stars), callback_data="pay_stars_final")],
            [InlineKeyboardButton(TEXTS["pay_usd"].format(price=price_usd), callback_data="pay_usd_final")],
            [InlineKeyboardButton(TEXTS["back"], callback_data=f"prod_{p_id}")]
        ]
        await query.edit_message_text(TEXTS["select_payment"].format(product_name=t_data["name"], price=f"{price_stars}⭐/{price_usd}$"),
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif "pay_stars" in data:
        price = p_data["price"]["stars"] if "fixed" in data else p_data["tariffs"][context.user_data["current_tariff"]]["stars"]
        await query.edit_message_text(TEXTS["stars_instructions"].format(price=price, product_name=p_data["name"], username=MODEL_USERNAME),
                                      parse_mode="Markdown")

    elif "pay_usd" in data:
        price = p_data["price"]["usd"] if "fixed" in data else p_data["tariffs"][context.user_data["current_tariff"]]["usd"]
        keyboard = [
            [InlineKeyboardButton("💳 PayPal", url=PAYPAL_LINK)],
            [InlineKeyboardButton("🏦 Platform", url=PAYMENT_PLATFORM_LINK)],
            [InlineKeyboardButton(TEXTS["back"], callback_data=f"prod_{p_id}")]
        ]
        await query.edit_message_text(TEXTS["paypal_instructions"].format(price=price, product_name=p_data["name"], link=PAYPAL_LINK),
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    if not TOKEN: 
        print("Error: TOKEN not found in .env")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(show_products_menu, pattern="^back_to_prods$"))
    app.add_handler(CallbackQueryHandler(show_options, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(handle_payment, pattern="^(tarr_|pay_)"))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()