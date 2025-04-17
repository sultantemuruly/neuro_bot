import os
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Start"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "Welcome! Press 'Start' to begin.", reply_markup=reply_markup
    )


async def start_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="option_1")],
        [InlineKeyboardButton("Option 2", callback_data="option_2")],
        [InlineKeyboardButton("Option 3", callback_data="option_3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose an option:", reply_markup=reply_markup
    )


async def button_selection_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    option_selected = query.data.split("_")[1]
    await query.edit_message_text(f"You selected option: {option_selected}")


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^Start$"), start_button_handler)
    )

    application.add_handler(
        CallbackQueryHandler(button_selection_handler, pattern="^option_")
    )

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
