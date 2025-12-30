import logging
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. Загрузка токена
load_dotenv()
TOKEN = os.getenv("TOKEN")

# 2. Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 3. Конфигурация и Ссылки
MODEL_USERNAME = "YourLovelyModelA"
PUBLIC_CHANNEL = "Bella_liii"
WELCOME_PHOTO = "https://i.ibb.co/m5mJxTLS/IMG-5752.jpg"
PAYPAL_LINK = "https://www.paypal.me"
PAYMENT_PLATFORM_LINK = "https://app.keepz.me/pay?qrType=DEFAULT&receiverType=USER&receiverId=2e9d8c7c-37f4-4b44-a4e2-7752e88248a1"

# 4. Данные о продуктах
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

# --- ФУНКЦИИ БОТА ---

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверка подписки на канал"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id=f"@{PUBLIC_CHANNEL}", user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking sub: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start - Отправляет Фото"""
    welcome_text = "🌟 *Hi, I'm Bella!* 🌟\n\nChoose an option below:"
    keyboard = [
        [InlineKeyboardButton("🔍 Check subscription", callback_data="check_sub")],
        [InlineKeyboardButton(f"💌 Message @{MODEL_USERNAME}", url=f"https://t.me/{MODEL_USERNAME}")]
    ]
    
    await update.message.reply_photo(
        photo=WELCOME_PHOTO,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def to_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в начало (удаляет текст, шлет фото)"""
    query = update.callback_query
    await query.answer()
    
    welcome_text = "🌟 *Hi, I'm Bella!* 🌟\n\nChoose an option below:"
    keyboard = [
        [InlineKeyboardButton("🔍 Check subscription", callback_data="check_sub")],
        [InlineKeyboardButton(f"💌 Message @{MODEL_USERNAME}", url=f"https://t.me/{MODEL_USERNAME}")]
    ]
    
    # Удаляем старое сообщение (так как нельзя превратить текст в фото)
    await query.message.delete()
    
    # Отправляем новое фото
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=WELCOME_PHOTO,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def check_subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка подписки и показ меню продуктов"""
    query = update.callback_query
    await query.answer("Checking...")
    
    is_member = await is_user_member(query.from_user.id, context)
    
    # Удаляем сообщение с фото (Start), чтобы прислать чистое меню
    await query.message.delete()

    if is_member:
        await send_products_menu(query.message.chat_id, context)
    else:
        keyboard = [
            [InlineKeyboardButton("✅ I subscribed", callback_data="check_sub")],
            [InlineKeyboardButton("📢 Go to channel", url=f"https://t.me/{PUBLIC_CHANNEL}")]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ You're not subscribed to @{PUBLIC_CHANNEL}\nPlease subscribe to continue.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def send_products_menu(chat_id, context):
    """Отправка меню выбора продуктов (Текстовое сообщение)"""
    keyboard = []
    for p_id, p_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(p_data["name"], callback_data=f"prod_{p_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Start", callback_data="to_start")])
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="Hi sweetie ❤️\nHere are my exclusive offers for you. Select a product:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_to_products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к списку продуктов (через редактирование текста)"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for p_id, p_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(p_data["name"], callback_data=f"prod_{p_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Start", callback_data="to_start")])
    
    await query.edit_message_text(
        text="Hi sweetie ❤️\nSelect a product:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_product_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ тарифов или выбор оплаты"""
    query = update.callback_query
    await query.answer()
    
    p_id = query.data.split('_')[1]
    p_data = PRODUCTS[p_id]
    context.user_data["current_product"] = p_id

    keyboard = []
    text = ""

    if "tariffs" in p_data:
        text = f"Select tariff for *{p_data['name']}*:"
        for t_id, t in p_data["tariffs"].items():
            keyboard.append([InlineKeyboardButton(f"{t['name']} - {t['stars']}⭐ / {t['usd']}$", callback_data=f"tarr_{t_id}")])
    else:
        text = f"*{p_data['name']}*\n\n{p_data['description']}\n\nChoose payment method:"
        keyboard.append([InlineKeyboardButton(f"⭐ Pay {p_data['price']['stars']} stars", callback_data="pay_stars_fixed")])
        keyboard.append([InlineKeyboardButton(f"💵 Pay {p_data['price']['usd']}$ USD", callback_data="pay_usd_fixed")])

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_prods")])
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора оплаты"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    p_id = context.user_data.get("current_product")
    p_data = PRODUCTS[p_id]
    
    # 1. Если выбрали Тариф -> предлагаем способ оплаты (Звезды или USD)
    if "tarr_" in data:
        t_id = data.split('_')[1]
        context.user_data["current_tariff"] = t_id
        t_data = p_data["tariffs"][t_id]
        
        text = f"Payment for: *{t_data['name']}*\nPrice: {t_data['stars']}⭐ or {t_data['usd']}$"
        keyboard = [
            [InlineKeyboardButton(f"⭐ Pay {t_data['stars']} Stars", callback_data="pay_stars_final")],
            [InlineKeyboardButton(f"💵 Pay {t_data['usd']}$ USD", callback_data="pay_usd_final")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"prod_{p_id}")]
        ]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    
    # 2. Оплата Звездами (Инструкция)
    elif "pay_stars" in data:
        # Определяем цену (фиксированная или тарифная)
        if "fixed" in data:
            price = p_data["price"]["stars"]
            back_callback = f"prod_{p_id}"
        else:
            price = p_data["tariffs"][context.user_data["current_tariff"]]["stars"]
            back_callback = f"tarr_{context.user_data['current_tariff']}"
            
        text = (
            f"🎁 *How to gift {price} stars:*\n\n"
            f"1. Go to my profile [@{MODEL_USERNAME}](https://t.me/{MODEL_USERNAME})\n"
            f"2. Tap 'Gift Stars' (top right menu)\n"
            f"3. Send exactly *{price}* stars\n"
            f"4. Send a screenshot here!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=back_callback)]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    # 3. Оплата USD (Ссылки)
    elif "pay_usd" in data:
        if "fixed" in data:
            price = p_data["price"]["usd"]
            back_callback = f"prod_{p_id}"
        else:
            price = p_data["tariffs"][context.user_data["current_tariff"]]["usd"]
            back_callback = f"tarr_{context.user_data['current_tariff']}"

        text = f"💳 *Pay {price}$ USD via links below:*"
        keyboard = [
            [InlineKeyboardButton("PayPal", url=PAYPAL_LINK)],
            [InlineKeyboardButton("Credit Card / Crypto", url=PAYMENT_PLATFORM_LINK)],
            [InlineKeyboardButton("🔙 Back", callback_data=back_callback)]
        ]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

def main():
    if not TOKEN:
        print("Error: TOKEN not found. Make sure .env file is created.")
        return

    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    
    # Меню и переходы
    app.add_handler(CallbackQueryHandler(check_subscription_handler, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(to_start_callback, pattern="^to_start$"))
    app.add_handler(CallbackQueryHandler(back_to_products_handler, pattern="^back_to_prods$"))
    
    # Товары и оплата
    app.add_handler(CallbackQueryHandler(show_product_options, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(handle_payment, pattern="^(tarr_|pay_)"))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()