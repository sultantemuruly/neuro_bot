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
from questions import questions_and_responses

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Prepare list of question keys (excluding transition_question if present)
question_keys = list(questions_and_responses.keys())
if "transition_question" in question_keys:
    question_keys.remove("transition_question")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reset user state
    context.user_data["question_index"] = 0
    context.user_data["history"] = []

    keyboard = [["Start"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Welcome! Press 'Start' to begin the conversation.",
        reply_markup=reply_markup,
    )


async def start_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_index"] = 0

    if "history" not in context.user_data:
        context.user_data["history"] = []

    await ask_next_question(update, context)


def get_scale_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(str(i), callback_data=f"scale_{i}")]
            for i in range(1, 6)
        ]
    )


async def ask_next_question(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("question_index", 0)

    if index < len(question_keys):
        key = question_keys[index]
        question_text = questions_and_responses[key]["question"]

        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(
                question_text, reply_markup=get_scale_keyboard()
            )
        else:
            await update_or_query.message.reply_text(
                question_text, reply_markup=get_scale_keyboard()
            )
    else:
        history = context.user_data.get("history", [])

        if not history:
            await update_or_query.message.reply_text("No conversation history found.")
            return

        formatted_history = "\n\n".join(
            [
                f"The bot asked: {entry['question']}\n"
                f"You selected: {entry['answer']}\n"
                f"The bot said: {entry['response']}"
                for entry in history
            ]
        )

        await update_or_query.message.reply_text(
            "✅ Thank you for answering all the questions!"
        )

        await update_or_query.message.reply_text(
            f"📝 *Your Conversation Summary:*\n\n{formatted_history}",
            parse_mode="Markdown",
        )


async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_value = query.data.split("_")[1]

    index = context.user_data.get("question_index", 0)

    if index < len(question_keys):
        key = question_keys[index]
        question_text = questions_and_responses[key]["question"]
        response_text = questions_and_responses[key]["response"]

        if "history" not in context.user_data:
            context.user_data["history"] = []

        context.user_data["history"].append(
            {
                "question": question_text,
                "answer": selected_value,
                "response": response_text,
            }
        )

        await query.edit_message_text(
            f"You selected: {selected_value}\n\n{response_text}"
        )

        # Move to next question
        context.user_data["question_index"] = index + 1
        await ask_next_question(query, context)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🔄 Your conversation has been reset. Send /start to begin again."
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^Start$"), start_button_handler)
    )
    application.add_handler(
        CallbackQueryHandler(button_selection_handler, pattern="^scale_")
    )

    print("🤖 Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
