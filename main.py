import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "8451967314:AAF11S9ehfxYWeHoQMI68xcjk0B9v6Nyd1M"
PUBLIC_CHANNEL = "Bella_liii"
PRIVATE_CHANNEL_LINK = "https://t.me/+sbgTGMOS93o4YmNi"
PAYPAL_LINK = "https://www.paypal.me"
PAYMENT_PLATFORM_LINK = "https://app.keepz.me/pay?qrType=DEFAULT&receiverType=USER&receiverId=2e9d8c7c-37f4-4b44-a4e2-7752e88248a1"
QR_CODE_IMAGE = "https://i.ibb.co/TxZSnnLz/image.png"

# Продукты и тарифы
PRODUCTS = {
    "vip": {
        "name": {"ru": "💎 VIP подписка", "en": "💎 VIP Subscription"},
        "tariffs": {
            "1month": {"stars": 250, "usd": 7, "name": {"ru": "1 месяц", "en": "1 month"}},
            "3months": {"stars": 550, "usd": 18, "name": {"ru": "3 месяца", "en": "3 months"}},
            "lifetime": {"stars": 1000, "usd": 30, "name": {"ru": "Навсегда", "en": "Lifetime"}}
        }
    },
    "chat": {
        "name": {"ru": "💬 Чат со мной", "en": "💬 Chat with me"},
        "price": {"stars": 100, "usd": 3},
        "description": {"ru": "Будь со мной всегда на связи", "en": "Always stay in touch with me"}
    },
    "private": {
        "name": {"ru": "🔞 Приват С2С", "en": "🔞 Private C2C"},
        "price": {"stars": 1700, "usd": 50},
        "description": {"ru": "Эксклюзивный приватный контент", "en": "Exclusive private content"}
    }
}

# Тексты
TEXTS = {
    "ru": {
        "start": "👋 Привет! Выберите язык:",
        "welcome": "Привет милый ❤️\nНиже ты увидишь мои эксклюзивные предложения:",
        "select_product": "Выбери продукт, который тебя интересует:",
        "select_tariff": "Выбери тариф для {product_name}:",
        "select_payment": "Выбери способ оплаты для {product_name}:\nСтоимость: {price}",
        "pay_stars": "⭐ {price} звёзд",
        "pay_usd": "💵 {price}$ (PayPal/Платформа)",
        "stars_instructions": "🎁 Как подарить {price} звёзд для '{product_name}':\n\n1. Перейди в мой профиль [BellaLi](https://t.me/Bella_Lii21)\n2. Нажми 'Подарить звёзды'\n3. Выбери {price} звёзд\n4. Пришли скриншот\n\nПосле проверки ты получишь доступ!",
        "payment_platform_instructions": "🏦 *Оплата через платформу*\n\n💳 *Доступные методы:*\n• Bank Payment\n• Crypto Payment\n\n📱 *QR код для оплаты:*\n\n🔗 *Или перейди по ссылке:* [Нажми здесь]({link})\n\n⚠️ После оплаты пришли скриншот подтверждения",
        "paypal_instructions": "💳 Оплати {price}$ за '{product_name}' через [PayPal]({link}) и пришли скриншот",
        "back": "🔙 Назад",
        "subscribe_first": "Для доступа необходимо подписаться на канал:",
        "checking": "🔍 Проверяем твою подписку...",
        "not_subscribed": "❌ Ты не подписан на канал @{channel}",
        "product_description": "\n\n{description}",
        "error": "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
    },
    "en": {
        "start": "👋 Hello! Choose language:",
        "welcome": "Hi sweetie ❤️\nHere are my exclusive offers for you:",
        "select_product": "Choose the product you're interested in:",
        "select_tariff": "Select tariff for {product_name}:",
        "select_payment": "Select payment method for {product_name}:\nPrice: {price}",
        "pay_stars": "⭐ {price} stars",
        "pay_usd": "💵 {price}$ (PayPal/Platform)",
        "stars_instructions": "🎁 How to gift {price} stars for '{product_name}':\n\n1. Visit my profile [BellaLil](https://t.me/Bella_Lii21)\n2. Tap 'Gift Stars'\n3. Select {price} stars\n4. Send screenshot\n\nAfter verification you'll get access!",
        "payment_platform_instructions": "🏦 *Payment via Platform*\n\n💳 *Available methods:*\n• Bank Payment\n• Crypto Payment\n\n📱 *QR code for payment:*\n\n🔗 *Or follow the link:* [Click here]({link})\n\n⚠️ After payment send confirmation screenshot",
        "paypal_instructions": "💳 Pay {price}$ for '{product_name}' via [PayPal]({link}) and send screenshot",
        "back": "🔙 Back",
        "subscribe_first": "To get access please subscribe to channel:",
        "checking": "🔍 Checking your subscription...",
        "not_subscribed": "❌ You're not subscribed to @{channel}",
        "product_description": "\n\n{description}",
        "error": "⚠️ An error occurred. Please try again later."
    }
}

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=f"@{PUBLIC_CHANNEL}",
            user_id=user_id
        )
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Subscription check error: {str(e)}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
    ]
    await update.message.reply_text(
        TEXTS["ru"]["start"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")],
        ]
        await query.edit_message_text(
            text=TEXTS[language]["start"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error in back_to_start: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="start_ru")]
            ])
        )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = query.data.split("_")[-1]
    context.user_data["language"] = language

    welcome_photo = "https://i.ibb.co/m5mJxTLS/IMG-5752.jpg"
    welcome_text = (
        "🌟 *Привет, я Bella!* 🌟\n\n"
        "Очень рада новому знакомству с тобой! 💖\n"
        "В моем боте ты найдешь эксклюзивный контент и особые предложения, "
        "которые точно тебя порадуют.\n\n"
        "Не стесняйся писать мне лично - всегда открыта для общения! 😊"
        if language == "ru" else
        "🌟 *Hi, I'm Bella!* 🌟\n\n"
        "So happy to meet you! 💖\n"
        "In my bot you'll find exclusive content and special offers "
        "that will definitely please you.\n\n"
        "Feel free to DM me anytime - I'm always open for communication! 😊"
    )

    try:
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=welcome_photo,
            caption=welcome_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🔍 Проверить подписку" if language == "ru" else "🔍 Check subscription",
                    callback_data=f"check_sub_{language}"
                )],
                [InlineKeyboardButton(
                    "💌 Написать Bella" if language == "ru" else "💌 Message Bella",
                    url="https://t.me/Bella_Lii21"
                )]
            ])
        )
        await query.message.delete()
    except Exception as e:
        logger.error(f"Error in set_language: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"start_{language}"
                )]
            ])
        )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    language = query.data.split("_")[-1]

    try:
        checking_msg = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["checking"]
        )

        is_member = await is_user_member(query.from_user.id, context)

        if not is_member:
            await asyncio.sleep(3)
            is_member = await is_user_member(query.from_user.id, context)

        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=checking_msg.message_id
        )

        if is_member:
            await show_products_menu(query, context, language)
        else:
            keyboard = [
                [InlineKeyboardButton(
                    "✅ Я подписался" if language == "ru" else "✅ I subscribed",
                    callback_data=f"check_sub_{language}"
                )],
                [InlineKeyboardButton(
                    "📢 Перейти в канал" if language == "ru" else "📢 Go to channel",
                    url=f"https://t.me/{PUBLIC_CHANNEL}"
                )],
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"start_{language}"
                )]
            ]

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{TEXTS[language]['not_subscribed'].format(channel=PUBLIC_CHANNEL)}\n\n"
                     f"ℹ️ Если вы подписаны, но видите это сообщение:\n"
                     f"1. Убедитесь, что подписаны на @{PUBLIC_CHANNEL}\n"
                     f"2. Попробуйте выйти и зайти снова в канал\n"
                     f"3. Подождите 2-3 минуты и нажмите '✅ Я подписался'",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        logger.error(f"Subscription check error: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"start_{language}"
                )
            ]])
        )

async def show_products_menu(query, context: ContextTypes.DEFAULT_TYPE, language: str):
    try:
        keyboard = []
        for product_id, product_data in PRODUCTS.items():
            product_name = product_data["name"][language]
            description = product_data.get("description", {}).get(language, "")

            btn_text = product_name
            if description:
                btn_text += f" - {description.split('.')[0]}"

            keyboard.append([InlineKeyboardButton(
                btn_text,
                callback_data=f"product_{product_id}_{language}"
            )])

        keyboard.append([InlineKeyboardButton(
            TEXTS[language]["back"],
            callback_data=f"start_{language}"
        )])

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["welcome"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error in show_products_menu: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"start_{language}"
                )
            ]])
        )

async def show_product_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        parts = query.data.split('_')
        product_id = parts[1]
        language = parts[-1]

        product_data = PRODUCTS.get(product_id)
        if not product_data:
            raise ValueError(f"Product not found: {product_id}")

        context.user_data["current_product"] = product_id

        if "tariffs" in product_data:
            keyboard = []
            for tariff_id, tariff_data in product_data["tariffs"].items():
                tariff_name = tariff_data["name"][language]
                stars = tariff_data["stars"]
                usd = tariff_data["usd"]

                keyboard.append([InlineKeyboardButton(
                    f"{tariff_name} - {stars}⭐/{usd}$",
                    callback_data=f"tariff_{tariff_id}_{language}"
                )])

            keyboard.append([InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"products_{language}"
            )])

            await query.edit_message_text(
                text=TEXTS[language]["select_tariff"].format(product_name=product_data["name"][language]),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            price_text = f"{product_data['price']['stars']}⭐ или {product_data['price']['usd']}$"
            description = product_data.get("description", {}).get(language, "")

            message_text = f"{product_data['name'][language]}\n{price_text}"
            if description:
                message_text += TEXTS[language]["product_description"].format(description=description)

            keyboard = [
                [InlineKeyboardButton(
                    TEXTS[language]["pay_stars"].format(price=product_data["price"]["stars"]),
                    callback_data=f"pay_stars_fixed_{language}"
                )],
                [InlineKeyboardButton(
                    TEXTS[language]["pay_usd"].format(price=product_data["price"]["usd"]),
                    callback_data=f"pay_usd_fixed_{language}"
                )],
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )]
            ]

            await query.edit_message_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error in show_product_options: {str(e)}")
        language = parts[-1] if len(parts) > 1 else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS.get(language, {}).get("error", "⚠️ Error occurred"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS.get(language, {}).get("back", "🔙 Back"),
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        await show_products_menu(query, context, language)
    except Exception as e:
        logger.error(f"Error in back_to_products: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🔙 Назад",
                    callback_data="start_ru"
                )
            ]])
        )

async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        data = query.data.split("_")
        tariff_id = data[1]
        language = data[2]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data or "tariffs" not in product_data:
            raise ValueError("Invalid product data")

        tariff_data = product_data["tariffs"].get(tariff_id)
        if not tariff_data:
            raise ValueError("Tariff not found")

        context.user_data["current_tariff"] = tariff_id

        price_text = f"{tariff_data['stars']}⭐ или {tariff_data['usd']}$"

        keyboard = [
            [InlineKeyboardButton(
                TEXTS[language]["pay_stars"].format(price=tariff_data["stars"]),
                callback_data=f"pay_stars_{language}"
            )],
            [InlineKeyboardButton(
                TEXTS[language]["pay_usd"].format(price=tariff_data["usd"]),
                callback_data=f"pay_usd_{language}"
            )],
            [InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"product_{product_id}_{language}"
            )]
        ]

        await query.edit_message_text(
            text=TEXTS[language]["select_payment"].format(
                product_name=product_data["name"][language],
                price=price_text
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in show_payment_options: {str(e)}")
        language = "ru" if len(data) < 3 else data[2]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_stars_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data:
            raise ValueError("Product not found")

        price = product_data["price"]["stars"]

        await query.edit_message_text(
            text=TEXTS[language]["stars_instructions"].format(
                price=price,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"product_{product_id}_{language}"
                )]
            ])
        )
    except Exception as e:
        logger.error(f"Error in pay_with_stars_fixed: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_usd_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data:
            raise ValueError("Product not found")

        price = product_data["price"]["usd"]

        keyboard = [
            [InlineKeyboardButton(
                "💳 PayPal",
                callback_data=f"pay_paypal_fixed_{language}"
            )],
            [InlineKeyboardButton(
                "🏦 Bank Payment | Crypto Payment",
                callback_data=f"pay_platform_fixed_{language}"
            )],
            [InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"product_{product_id}_{language}"
            )]
        ]

        await query.edit_message_text(
            text=TEXTS[language]["select_payment"].format(
                product_name=product_data["name"][language],
                price=f"{price}$"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in pay_with_usd_fixed: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_platform_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data:
            raise ValueError("Product not found")

        price = product_data["price"]["usd"]

        keyboard = [
            [InlineKeyboardButton(
                "🏦 Перейти к оплате",
                url=PAYMENT_PLATFORM_LINK
            )],
            [InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"pay_usd_fixed_{language}"
            )]
        ]

        # Отправляем фото с QR кодом и инструкциями
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=QR_CODE_IMAGE,
            caption=TEXTS[language]["payment_platform_instructions"].format(
                price=price,
                link=PAYMENT_PLATFORM_LINK,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.message.delete()
    except Exception as e:
        logger.error(f"Error in pay_with_platform_fixed: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_paypal_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data:
            raise ValueError("Product not found")

        price = product_data["price"]["usd"]

        await query.edit_message_text(
            text=TEXTS[language]["paypal_instructions"].format(
                price=price,
                link=PAYPAL_LINK,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"pay_usd_fixed_{language}"
                )]
            ])
        )
    except Exception as e:
        logger.error(f"Error in pay_with_paypal_fixed: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data or "tariffs" not in product_data:
            raise ValueError("Invalid product data")

        tariff_id = context.user_data.get("current_tariff")
        if not tariff_id:
            raise ValueError("Tariff ID not found in context.user_data")

        tariff_data = product_data["tariffs"].get(tariff_id)
        if not tariff_data:
            raise ValueError("Tariff not found")

        price = tariff_data["stars"]

        await query.edit_message_text(
            text=TEXTS[language]["stars_instructions"].format(
                price=price,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"tariff_{tariff_id}_{language}"
                )]
            ])
        )
    except Exception as e:
        logger.error(f"Error in pay_with_stars: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_usd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data or "tariffs" not in product_data:
            raise ValueError("Invalid product data")

        tariff_id = context.user_data.get("current_tariff")
        if not tariff_id:
            raise ValueError("Tariff ID not found in context.user_data")

        tariff_data = product_data["tariffs"].get(tariff_id)
        if not tariff_data:
            raise ValueError("Tariff not found")

        price = tariff_data["usd"]

        keyboard = [
            [InlineKeyboardButton(
                "💳 PayPal",
                callback_data=f"pay_paypal_{language}"
            )],
            [InlineKeyboardButton(
                "🏦 Bank Payment | Crypto Payment",
                callback_data=f"pay_platform_{language}"
            )],
            [InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"tariff_{tariff_id}_{language}"
            )]
        ]

        await query.edit_message_text(
            text=TEXTS[language]["select_payment"].format(
                product_name=product_data["name"][language],
                price=f"{price}$"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in pay_with_usd: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data or "tariffs" not in product_data:
            raise ValueError("Invalid product data")

        tariff_id = context.user_data.get("current_tariff")
        if not tariff_id:
            raise ValueError("Tariff ID not found in context.user_data")

        tariff_data = product_data["tariffs"].get(tariff_id)
        if not tariff_data:
            raise ValueError("Tariff not found")

        price = tariff_data["usd"]

        keyboard = [
            [InlineKeyboardButton(
                "🏦 Перейти к оплате" if language == "ru" else "🏦 Go to payment",
                url=PAYMENT_PLATFORM_LINK
            )],
            [InlineKeyboardButton(
                TEXTS[language]["back"],
                callback_data=f"pay_usd_{language}"
            )]
        ]

        # Отправляем фото с QR кодом и инструкциями
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=QR_CODE_IMAGE,
            caption=TEXTS[language]["payment_platform_instructions"].format(
                price=price,
                link=PAYMENT_PLATFORM_LINK,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.message.delete()
    except Exception as e:
        logger.error(f"Error in pay_with_platform: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

async def pay_with_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        language = query.data.split("_")[-1]
        product_id = context.user_data.get("current_product")

        if not product_id:
            raise ValueError("Product ID not found in context.user_data")

        product_data = PRODUCTS.get(product_id)
        if not product_data or "tariffs" not in product_data:
            raise ValueError("Invalid product data")

        tariff_id = context.user_data.get("current_tariff")
        if not tariff_id:
            raise ValueError("Tariff ID not found in context.user_data")

        tariff_data = product_data["tariffs"].get(tariff_id)
        if not tariff_data:
            raise ValueError("Tariff not found")

        price = tariff_data["usd"]

        await query.edit_message_text(
            text=TEXTS[language]["paypal_instructions"].format(
                price=price,
                link=PAYPAL_LINK,
                product_name=product_data["name"][language]
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"pay_usd_{language}"
                )]
            ])
        )
    except Exception as e:
        logger.error(f"Error in pay_with_paypal: {str(e)}")
        language = query.data.split("_")[-1] if "_" in query.data else "ru"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS[language]["error"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    TEXTS[language]["back"],
                    callback_data=f"products_{language}"
                )
            ]])
        )

def main():
    app = Application.builder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    app.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_sub_"))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern="^start_"))
    app.add_handler(CallbackQueryHandler(back_to_products, pattern="^products_"))
    app.add_handler(CallbackQueryHandler(show_product_options, pattern=r"^product_"))
    app.add_handler(CallbackQueryHandler(show_payment_options, pattern="^tariff_"))
    app.add_handler(CallbackQueryHandler(pay_with_stars_fixed, pattern="^pay_stars_fixed_"))
    app.add_handler(CallbackQueryHandler(pay_with_usd_fixed, pattern="^pay_usd_fixed_"))
    app.add_handler(CallbackQueryHandler(pay_with_paypal_fixed, pattern="^pay_paypal_fixed_"))
    app.add_handler(CallbackQueryHandler(pay_with_platform_fixed, pattern="^pay_platform_fixed_"))
    app.add_handler(CallbackQueryHandler(pay_with_stars, pattern="^pay_stars_"))
    app.add_handler(CallbackQueryHandler(pay_with_usd, pattern="^pay_usd_"))
    app.add_handler(CallbackQueryHandler(pay_with_paypal, pattern="^pay_paypal_"))
    app.add_handler(CallbackQueryHandler(pay_with_platform, pattern="^pay_platform_"))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()