import os
import random
import logging
from typing import List, Optional, Tuple

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")


curiosity_templates = [
    [
        ["I noticed", "I saw", "I found", "A quick look showed", "I came across"],
        ["something new", "a small change", "something different", "an update", "something interesting"],
        ["today", "just now", "earlier", "recently"],
        ["See below", "Check the comments", "Look below", "Have a quick look"],
    ],
    [
        ["At first I almost missed it", "I wasn’t expecting this", "I checked for a second"],
        ["but something changed", "and found an update", "and noticed a difference"],
        ["Look below", "See the comments", "Take a look below"],
    ],
]

direct_templates = [
    [
        ["New update is live", "Latest update is here", "Fresh post is up", "Today’s update is ready"],
        ["Check below", "See the comments", "Take a look", "Look below now"],
    ],
    [
        ["There’s a new post now", "New content is available", "The latest one is up"],
        ["Look below", "Open the comments", "View the update below"],
    ],
]

normal_templates = [
    [
        ["New post today", "Fresh content today", "There’s something new", "A new update is available"],
        ["Have a look", "See below", "Take a quick look", "Check it out"],
    ],
    [
        ["Posted something new today", "Shared a new update", "Added a fresh post"],
        ["Take a look", "See below", "Look in the comments"],
    ],
]

last_opening: Optional[str] = None
last_closing: Optional[str] = None


def pick_choice(pool: List[str], avoid: Optional[str] = None) -> str:
    items = pool[:]
    random.shuffle(items)
    if avoid in items and len(items) > 1:
        items.remove(avoid)
    return random.choice(items)


def build_post(template_group: List[List[List[str]]]) -> str:
    global last_opening, last_closing

    template = random.choice(template_group)
    parts = []

    for idx, choices in enumerate(template):
        if idx == 0:
            choice = pick_choice(choices, last_opening)
        elif idx == len(template) - 1:
            choice = pick_choice(choices, last_closing)
        else:
            choice = random.choice(choices)
        parts.append(choice)

    last_opening = parts[0]
    last_closing = parts[-1]

    if len(parts) == 4:
        line1 = f"{parts[0]} {parts[1]} {parts[2]}"
        line2 = parts[3]
    elif len(parts) == 3:
        line1 = f"{parts[0]} {parts[1]}"
        line2 = parts[2]
    else:
        line1 = " ".join(parts[:-1])
        line2 = parts[-1]

    return f"{line1}\n{line2}".strip()


def get_category_templates(text: str):
    if text == "بوستات فضول":
        return curiosity_templates
    if text == "بوستات مباشرة":
        return direct_templates
    if text == "بوستات عادية":
        return normal_templates
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["بوستات فضول", "بوستات مباشرة"],
        ["بوستات عادية"],
    ]
    await update.message.reply_text(
        "اختر نوع البوست:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    templates = get_category_templates(text)

    if not templates:
        await update.message.reply_text("اكتب /start ثم اختر نوع البوست")
        return

    post = build_post(templates)
    await update.message.reply_text(post)


def main():
    logger.info("Starting Telegram bot...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
