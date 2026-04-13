import asyncio
import os
import re
import random
import itertools

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

# ---------------------------
# EXPANDED CONTENT
# ---------------------------
LINE1_OPTIONS = [
    "I wasn’t even looking for this",
    "I almost skipped checking today",
    "Didn’t expect anything new today",
    "Was just scrolling for a second",
    "Opened the app randomly",
    "I was only checking for a moment",
    "Didn’t plan to look again today",
    "I wasn’t expecting anything different",
    "I almost ignored this completely",
    "Was just passing by quickly",
    "I checked again out of curiosity",
    "Didn’t think anything fresh was there",
    "I opened it without expecting much",
    "I was just taking a quick look",
    "I almost moved on without checking",
    "This caught me by surprise today",
    "I wasn’t planning to stop here",
    "I gave it one quick look",
    "I checked only for a second",
    "I nearly missed this update",
]

CONNECTORS = [
    "",
    "…",
    "and then",
    "but",
    "when suddenly",
    "and somehow",
    "then",
    "before I left",
    "just now",
    "a second later",
]

LINE2_OPTIONS = [
    "something new showed up while scrolling",
    "something unexpected appeared",
    "I noticed a small change",
    "something felt different this time",
    "I saw something I didn’t expect",
    "something caught my attention",
    "a small update appeared",
    "I ended up noticing something new",
    "there was a change I didn’t expect",
    "something unusual popped up",
    "I found a fresh update",
    "there was something worth checking",
    "I spotted something new right away",
    "something interesting appeared",
    "a new change was sitting there",
    "I noticed a fresh detail",
    "there was a small surprise waiting",
    "I ran into something different",
    "I found something I almost missed",
    "there was a quick update sitting there",
]

ENDINGS = [
    "",
    "😅",
    "👀",
    "🤔",
    "😄",
    "😮",
    "🔥",
    "✨",
    "🙃",
    "✅",
    "📌",
]

OPENERS = [
    "",
    "Looks worth checking.",
    "This one stood out.",
    "That was unexpected.",
    "Definitely caught my eye.",
    "Might be worth a look.",
    "This feels different.",
    "That was a nice surprise.",
    "Worth seeing once.",
]

# ---------------------------
# STATE
# ---------------------------
ALL_POSTS: list[str] = []
USED_POSTS: set[str] = set()
AVAILABLE_POSTS: list[str] = []


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_all_posts() -> list[str]:
    posts = set()

    for line1, connector, line2, ending, opener in itertools.product(
        LINE1_OPTIONS,
        CONNECTORS,
        LINE2_OPTIONS,
        ENDINGS,
        OPENERS,
    ):
        parts = [line1]

        if connector:
            parts.append(connector)

        parts.append(line2)

        first_line = " ".join(parts).strip()

        if ending:
            first_line = f"{first_line} {ending}"

        if opener:
            post = f"{first_line}\n{opener}"
        else:
            post = first_line

        posts.add(clean_text(post))

    posts_list = list(posts)
    random.shuffle(posts_list)
    return posts_list


def reset_available_posts() -> None:
    global AVAILABLE_POSTS
    AVAILABLE_POSTS = ALL_POSTS.copy()
    random.shuffle(AVAILABLE_POSTS)


def get_unique_post() -> str:
    global AVAILABLE_POSTS, USED_POSTS

    if not AVAILABLE_POSTS:
        USED_POSTS.clear()
        reset_available_posts()

    while AVAILABLE_POSTS:
        post = AVAILABLE_POSTS.pop()
        if post not in USED_POSTS:
            USED_POSTS.add(post)
            return post

    # Fallback safety
    USED_POSTS.clear()
    reset_available_posts()
    post = AVAILABLE_POSTS.pop()
    USED_POSTS.add(post)
    return post


def build_keyboard(post_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Generate Post 🔥", callback_data="generate_post")],
            [InlineKeyboardButton("Copy Post 📋", copy_text=CopyTextButton(text=post_text))],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = get_unique_post()
    text = (
        "Welcome.\n\n"
        "Press the button below to generate a unique post.\n\n"
        f"{post}"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=build_keyboard(post),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = get_unique_post()
    text = (
        "Use the buttons below.\n\n"
        f"{post}"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=build_keyboard(post),
    )


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = get_unique_post()
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
        post = get_unique_post()
        await query.edit_message_text(
            text=post,
            reply_markup=build_keyboard(post),
        )


def main() -> None:
    global ALL_POSTS

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Add it in Railway Variables.")

    ALL_POSTS = build_all_posts()
    reset_available_posts()

    print(f"Total unique posts loaded: {len(ALL_POSTS)}")

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
