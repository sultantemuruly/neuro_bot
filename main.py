import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from handlers import (
    start,
    reset,
    start_button_handler,
    button_selection_handler,
    new_conversation_handler,
)


def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^Start$"), start_button_handler)
    )
    application.add_handler(
        CallbackQueryHandler(button_selection_handler, pattern="^scale_")
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^New Conversation$"), new_conversation_handler
        )
    )

    print("🤖 Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
