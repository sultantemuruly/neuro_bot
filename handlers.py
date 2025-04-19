from telegram.ext import ContextTypes
from keyboards import (
    get_scale_keyboard,
    get_start_keyboard,
    get_new_conversation_keyboard,
)
from questions import questions_and_responses
from ai import get_recommendations
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

# Prepare list of question keys
question_keys = list(questions_and_responses.keys())
if "transition_question" in question_keys:
    question_keys.remove("transition_question")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reset user state
    context.user_data["question_index"] = 0
    context.user_data["history"] = []

    reply_markup = get_start_keyboard()

    await update.message.reply_text(
        "👋 Welcome! Press 'Start' to begin the conversation.",
        reply_markup=reply_markup,
    )


async def start_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_index"] = 0
    if "history" not in context.user_data:
        context.user_data["history"] = []

    await update.message.reply_text(
        "Starting conversation... Please use the buttons to respond.",
        reply_markup=ReplyKeyboardRemove(),
    )

    await ask_next_question(update, context)


async def ask_next_question(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("question_index", 0)

    if index < len(question_keys):
        key = question_keys[index]
        question_text = questions_and_responses[key]["question"]

        message = (
            update_or_query.message
            if isinstance(update_or_query, Update)
            else update_or_query.message
        )
        await message.reply_text(question_text, reply_markup=get_scale_keyboard())
    else:
        await _show_summary(update_or_query, context)


async def _show_summary(update_or_query, context: ContextTypes.DEFAULT_TYPE):
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
        "Thank you for answering all the questions!"
    )
    await update_or_query.message.reply_text(
        f"*Your Conversation Summary:*\n\n{formatted_history}",
        parse_mode="Markdown",
    )

    # Get and send ai recommendations
    recommendations = await get_recommendations(history)
    await update_or_query.message.reply_text(
        f"*Personal Recommendations:*\n\n{recommendations}",
        parse_mode="Markdown",
    )

    reply_markup = get_new_conversation_keyboard()

    await update_or_query.message.reply_text(
        "Conversation complete! You can now type a message or start a new conversation.",
        reply_markup=reply_markup,
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
            f"{question_text}\n\n(You selected: {selected_value})"
        )

        await query.message.reply_text(response_text)

        context.user_data["question_index"] = index + 1
        await ask_next_question(query, context)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Your conversation has been reset. Send /start to begin again."
    )


async def new_conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
