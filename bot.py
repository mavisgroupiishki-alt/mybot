import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)
from config import BOT_TOKEN, ADMIN_CHAT_ID, VIDEO_LIBRARY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
(ASK_NAME, ASK_COMPANY, ASK_PHONE, MAIN_MENU,
 CB_NAME, CB_PHONE, CB_QUESTION, CB_TIME) = range(8)


async def send_telegram_notification(context, user_data):
    try:
        username = user_data.get("username", "нет")
        username_str = f"@{username}" if username != "нет" else "нет username"
        text = (
            "🔔 *Новая регистрация!*\n"
            "─────────────────\n"
            f"👤 *Имя:* {user_data.get('name', '—')}\n"
            f"🏢 *Компания:* {user_data.get('company', '—')}\n"
            f"📞 *Телефон:* {user_data.get('phone', '—')}\n"
            f"💬 *Telegram:* {username_str}\n"
            f"🆔 *ID:* `{user_data.get('telegram_id', '—')}`"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


async def send_callback_notification(context, user_data):
    try:
        username = user_data.get("username", "нет")
        username_str = f"@{username}" if username != "нет" else "нет username"
        text = (
            "📞 *Заявка на консультацию!*\n"
            "─────────────────\n"
            f"👤 *Имя:* {user_data.get('cb_name', '—')}\n"
            f"📞 *Телефон:* {user_data.get('cb_phone', '—')}\n"
            f"❓ *Вопрос:* {user_data.get('cb_question', '—')}\n"
            f"🕐 *Удобное время:* {user_data.get('cb_time', '—')}\n"
            f"🎯 *Тема просмотра:* {user_data.get('last_topic', '—')}\n"
            f"💬 *Telegram:* {username_str}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send callback notification: {e}")


def get_topics_keyboard():
    topics = list(VIDEO_LIBRARY.keys())
    keyboard = []
    for i in range(0, len(topics), 2):
        keyboard.append(topics[i:i + 2])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_time_keyboard():
    """Кнопки с вариантами удобного времени (9:00 – 18:00)."""
    keyboard = ReplyKeyboardMarkup([
        ["🕙 9:00 – 11:00", "🕚 11:00 – 13:00"],
        ["🕐 13:00 – 15:00", "🕒 15:00 – 18:00"],
        ["📅 В любое время (9:00 – 18:00)"],
    ], resize_keyboard=True)
    return keyboard


def get_after_video_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Оставить заявку на консультацию", callback_data="request_callback")],
        [InlineKeyboardButton("🎬 Выбрать другую тему", callback_data="choose_topic")],
    ])


def find_topic(text):
    text = text.strip().lower()
    for key in VIDEO_LIBRARY:
        if text == key.lower():
            return key
    for key in VIDEO_LIBRARY:
        if text in key.lower() or key.lower() in text:
            return key
    for key in VIDEO_LIBRARY:
        for word in text.split():
            if len(word) >= 3 and word in key.lower():
                return key
    return None


# ─── РЕГИСТРАЦИЯ ───────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Прежде чем начать, пожалуйста, заполните небольшую форму.\n\n"
        "Как вас зовут? (Имя и фамилия)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Без компании", callback_data="no_company")]])
    await update.message.reply_text(
        f"Отлично, {context.user_data['name']}! 👍\n\n"
        "Укажите название вашей компании\n"
        "_(или нажмите кнопку ниже, если вы не представляете компанию)_",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return ASK_COMPANY


async def ask_company_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["company"] = update.message.text.strip()
    await update.message.reply_text("📞 Введите ваш номер телефона:", reply_markup=ReplyKeyboardRemove())
    return ASK_PHONE


async def ask_company_no_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["company"] = "Без компании"
    await query.edit_message_text("✅ Понял, без компании.")
    await query.message.reply_text("📞 Введите ваш номер телефона:")
    return ASK_PHONE


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text.strip()
    context.user_data["telegram_id"] = update.effective_user.id
    context.user_data["username"] = update.effective_user.username or "нет"
    await send_telegram_notification(context, context.user_data)
    await update.message.reply_text(
        "✅ *Данные сохранены!*\n\n"
        "Теперь выберите тему из меню ниже или напишите ключевое слово "
        "(например: *аттестация*, *охрана труда*).\n\n"
        "Я пришлю вам короткий видео-гайд по этой теме. 🎬",
        parse_mode="Markdown",
        reply_markup=get_topics_keyboard(),
    )
    return MAIN_MENU


# ─── ГЛАВНОЕ МЕНЮ ──────────────────────────────────────────

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text.strip()
    matched_key = find_topic(user_text)

    if matched_key:
        context.user_data["last_topic"] = matched_key
        video_info = VIDEO_LIBRARY[matched_key]

        await update.message.reply_text(
            f"🎬 *{matched_key}*\n\n{video_info['description']}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )

        video = video_info.get("video")
        if video:
            try:
                await update.message.reply_video(video=video, caption=f"📌 {matched_key}")
            except Exception as e:
                logger.error(f"Could not send video: {e}")
                fallback = video_info.get("fallback_url", video)
                await update.message.reply_text(f"📎 Ссылка на видео:\n{fallback}")
        else:
            await update.message.reply_text("⏳ Видео по этой теме скоро будет добавлено.")

        await update.message.reply_text(
            "Что хотите сделать дальше?",
            reply_markup=get_after_video_keyboard(),
        )
    else:
        topics_list = "\n".join(f"• {k}" for k in VIDEO_LIBRARY.keys())
        await update.message.reply_text(
            f"🤔 По запросу *«{user_text}»* ничего не найдено.\n\n"
            f"Доступные темы:\n{topics_list}\n\n"
            "Выберите из меню или напишите другое ключевое слово.",
            parse_mode="Markdown",
            reply_markup=get_topics_keyboard(),
        )

    return MAIN_MENU


async def handle_after_video_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "choose_topic":
        await query.edit_message_text("Выберите тему 👇")
        await query.message.reply_text(
            "Выберите тему из меню:",
            reply_markup=get_topics_keyboard(),
        )
        return MAIN_MENU

    elif query.data == "request_callback":
        await query.edit_message_text(
            "📞 *Заявка на консультацию*\n\n"
            "Шаг 1 из 4\n\n"
            "Как вас зовут? (Имя и фамилия)",
            parse_mode="Markdown",
        )
        return CB_NAME

    return MAIN_MENU


# ─── ФОРМА ОБРАТНОЙ СВЯЗИ ──────────────────────────────────

async def cb_ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cb_name"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 2 из 4\n\n"
        "📞 Введите ваш номер телефона:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CB_PHONE


async def cb_ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cb_phone"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 3 из 4\n\n"
        "❓ Какой вопрос вас интересует?",
    )
    return CB_QUESTION


async def cb_ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cb_question"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 4 из 4\n\n"
        "🕐 В какое время вам удобнее перезвонить?\n\n"
        "Мы работаем с 9:00 до 18:00. Выберите удобный интервал или напишите конкретное время:",
        reply_markup=get_time_keyboard(),
    )
    return CB_TIME


async def cb_ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cb_time"] = update.message.text.strip()

    await send_callback_notification(context, context.user_data)

    await update.message.reply_text(
        "✅ *Заявка принята!*\n\n"
        "Мы свяжемся с вами в ближайшее время. 🙌",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        "Что хотите сделать дальше?",
        reply_markup=get_after_video_keyboard(),
    )
    return MAIN_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Диалог завершён. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ─── MAIN ──────────────────────────────────────────────────

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_COMPANY: [
                CallbackQueryHandler(ask_company_no_company, pattern="^no_company$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company_text),
            ],
            ASK_PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            MAIN_MENU:   [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic),
                CallbackQueryHandler(handle_after_video_buttons, pattern="^(choose_topic|request_callback)$"),
            ],
            CB_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_ask_name)],
            CB_PHONE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_ask_phone)],
            CB_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_ask_question)],
            CB_TIME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_ask_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(conv_handler)
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
