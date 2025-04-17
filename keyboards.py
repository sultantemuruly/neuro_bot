from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_start_keyboard():
    keyboard = [["Start"]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def get_scale_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(str(i), callback_data=f"scale_{i}")]
            for i in range(1, 6)
        ]
    )
