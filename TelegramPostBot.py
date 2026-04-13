import asyncio
import os
import re
import random

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

LINE1_SPIN = r"""
({I wasn’t even looking for this|I almost skipped checking today|Didn’t expect anything new today|Was just scrolling for a second|Opened the app randomly|I was only checking for a moment|Didn’t plan to look again today|I wasn’t expecting anything different|I almost ignored this completely|Was just passing by quickly}
{ |…|}
)
"""

LINE2_SPIN = r"""
({but something new showed up while scrolling|and something unexpected appeared|and I noticed a small change|but something felt different this time|and I saw something I didn’t expect|but something caught my attention|and a small update appeared|but I ended up noticing something new|and there was a change I didn’t expect|but something unusual popped up}
)
"""

EMOJIS = ["😅", "👀", "🤔", "😄", "😮", "🔥", "✨", "🙃"]


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_top_level_blocks(text: str) -> list[str]:
    blocks = []
    depth = 0
    current = []

    for ch in text:
        if ch == "(":
            if depth == 0:
                current = []
            depth += 1
            current.append(ch)
        elif ch == ")":
            if depth > 0:
                current.append(ch)
                depth -= 1
                if depth == 0:
                    block = "".join(current).strip()
                    if block:
                        blocks.append(block)
        else:
            if depth > 0:
                current.append(ch)

    return blocks


def expand_spin(segment: str) -> str:
    pattern = re.compile(r"\{([^{}]*)\}")

    while True:
        match = pattern.search(segment)
        if not match:
            break

        choices = match.group(1).split("|")
        replacement = random.choice(choices)
        segment = segment[:match.start()] + replacement + segment[match.end():]

    return clean_text(segment)


def generate_from_spin(spin_text: str) -> str:
    blocks = split_top_level_blocks(spin_text)
    if not blocks:
        return ""

    block = random.choice(blocks)
    block_content = block.strip()

    if block_content.startswith("(") and block_content.endswith(")"):
        block_content = block_content[1:-1]

    return clean_text(expand_spin(block_content))


def generate_single_post() -> str:
    line1 = generate_from_spin(LINE1_SPIN)
    line2 = generate_from_spin(LINE2_SPIN)

    if random.random() < 0.85 and not any(emoji in line2 for emoji in EMOJIS):
        line2 += " " + random.choice(EMOJIS)

    return clean_text(f"{line1}\n{line2}")


def build_keyboard(post_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Generate Post 🔥", callback_data="generate_post")],
            [InlineKeyboardButton("Copy Post 📋", copy_text=CopyTextButton(text=post_text))],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = generate_single_post()
    text = (
        "Welcome.\n\n"
        "Press the button below to generate a post.\n\n"
        f"{post}"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=build_keyboard(post),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = generate_single_post()
    text = (
        "Use the buttons below.\n\n"
        f"{post}"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=build_keyboard(post),
    )


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = generate_single_post()
    await update.message.reply_text(
        text=post,
        reply_markup=build_keyboard(post),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    if query.data == "generate_post":
        post = generate_single_post()
        await query.edit_message_text(
            text=post,
            reply_markup=build_keyboard(post),
        )


def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Add it in Railway Variables.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
