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

# =========================
# CONTENT BANK
# =========================

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
    "I opened it without expecting much",
    "I was just taking a quick look",
    "I almost moved on without checking",
    "This caught me by surprise today",
    "I wasn’t planning to stop here",
    "I gave it one quick look",
    "I checked only for a second",
    "I nearly missed this update",
    "I checked back for a moment",
    "I was about to move on",
    "I just stopped here briefly",
    "I came across this by chance",
    "I only meant to check quickly",
    "I was not planning to stay long",
    "I looked again just for a second",
    "I dropped in for a quick look",
    "I was just passing through here",
    "I opened this out of curiosity",
    "I checked once more and saw this",
    "I only took a fast look",
    "I came back for a second",
    "I checked this while scrolling",
    "I noticed this during a quick stop",
    "I wasn’t expecting this at all",
    "I happened to see this just now",
    "I was only here for a second",
    "I took another quick look today",
    "I ended up checking again",
    "I was just browsing around",
    "I almost missed this completely",
    "I found this during a quick visit",
    "I checked in again for a moment",
    "I looked at this one more time",
    "I opened this on a whim",
    "I landed here by accident",
    "I gave this a quick glance",
    "I happened to open this again",
    "I returned for a short look",
    "I barely stopped here",
    "I almost scrolled past this",
    "I took a quick peek here",
    "I checked again without expecting much",
    "I only paused here for a moment",
    "I came back and noticed this",
    "I found this unexpectedly",
    "I looked again just out of habit",
    "I didn’t think I would notice anything new",
]

CONNECTORS = [
    "",
    "and then",
    "but",
    "when suddenly",
    "and somehow",
    "then",
    "before I left",
    "a second later",
    "and right away",
    "before moving on",
    "after that",
    "and in that moment",
    "right there",
    "almost instantly",
    "and out of nowhere",
    "all of a sudden",
    "without warning",
    "before I closed it",
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
    "I spotted something new right away",
    "something interesting appeared",
    "a new change was sitting there",
    "I noticed a fresh detail",
    "there was a small surprise waiting",
    "I ran into something different",
    "I found something I almost missed",
    "there was a quick update sitting there",
    "a fresh detail caught my eye",
    "a small shift stood out immediately",
    "I noticed something different at once",
    "there was a new detail waiting there",
    "something better than expected appeared",
    "I came across something new",
    "a quick update showed up",
    "something changed more than I expected",
    "I noticed something fresh right away",
    "a small update stood out",
    "there was something new sitting there",
    "I saw a fresh detail pop up",
    "there was a change worth noticing",
    "a tiny update caught my eye",
    "something new appeared out of nowhere",
    "I picked up on a new detail",
    "there was something different right there",
    "a fresh change was easy to spot",
    "I found a detail I had not seen before",
    "there was a fresh change sitting there",
    "something new showed up unexpectedly",
    "there was something slightly different this time",
    "a new detail stood out fast",
    "I caught a fresh update while checking",
    "something I had not noticed before appeared",
    "there was a small change worth seeing",
    "a fresh little update appeared",
    "I noticed something new without trying",
    "there was something new hiding there",
    "something useful caught my eye",
    "I found something different this time",
    "a small detail made a difference",
    "something updated quietly in the background",
    "there was something fresh to notice",
    "a change appeared sooner than expected",
    "I spotted a new detail in seconds",
]

SOFT_OPENERS = [
    "",
    "That stood out.",
    "That felt different.",
    "That caught my eye.",
    "That was unexpected.",
    "This looked different.",
    "This one felt new.",
    "That was easy to notice.",
    "This stood out fast.",
    "That looked slightly off.",
    "Something there felt different.",
    "This was hard to miss.",
]

MICRO_ENDINGS = [
    "",
    "😅",
    "👀",
    "🤔",
    "😄",
    "😮",
    "🔥",
    "✨",
    "🙃",
]

USED_POSTS = set()


# =========================
# HELPERS
# =========================

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def maybe_emoji(text: str) -> str:
    emoji = random.choice(MICRO_ENDINGS)
    if emoji:
        return f"{text} {emoji}"
    return text


def build_candidate_parts() -> tuple[str, str, str, str]:
    line1 = random.choice(LINE1_OPTIONS)
    connector = random.choice(CONNECTORS)
    line2 = random.choice(LINE2_OPTIONS)
    opener = random.choice(SOFT_OPENERS)
    return line1, connector, line2, opener


def format_style_one(line1: str, connector: str, line2: str, opener: str) -> str:
    # سطرين طبيعيين
    first = line1
    second = f"{connector} {line2}".strip() if connector else line2
    second = maybe_emoji(second)
    return clean_text(f"{first}\n{second}")


def format_style_two(line1: str, connector: str, line2: str, opener: str) -> str:
    # سطر واحد
    parts = [line1]
    if connector:
        parts.append(connector)
    parts.append(line2)
    text = " ".join(parts)
    text = maybe_emoji(text)
    return clean_text(text)


def format_style_three(line1: str, connector: str, line2: str, opener: str) -> str:
    # سطر قصير + سطر ثاني مباشر
    first = line1
    second = line2
    second = maybe_emoji(second)
    return clean_text(f"{first}\n{second}")


def format_style_four(line1: str, connector: str, line2: str, opener: str) -> str:
    # سطرين مع opener خفيف
    first = opener if opener else line1
    second_parts = [line1]
    if connector:
        second_parts.append(connector)
    second_parts.append(line2)
    second = " ".join(second_parts)
    second = maybe_emoji(second)
    return clean_text(f"{first}\n{second}")


def format_style_five(line1: str, connector: str, line2: str, opener: str) -> str:
    # جملة قصيرة جدًا
    short = random.choice([
        line1,
        line2,
        f"{line1} {line2}",
        f"{line1} and {line2}",
    ])
    short = maybe_emoji(clean_text(short))
    return short


def format_style_six(line1: str, connector: str, line2: str, opener: str) -> str:
    # صياغة مختلفة تمامًا نسبيًا
    variants = [
        f"{line1}\n{line2}",
        f"{line1}\n{opener}" if opener else f"{line1}\n{line2}",
        f"{opener}\n{line2}" if opener else f"{line1}\n{line2}",
        f"{line1} {connector} {line2}".strip(),
    ]
    chosen = clean_text(random.choice(variants))
    return maybe_emoji(chosen)


def build_post_once() -> str:
    line1, connector, line2, opener = build_candidate_parts()

    style_builder = random.choice([
        format_style_one,
        format_style_two,
        format_style_three,
        format_style_four,
        format_style_five,
        format_style_six,
    ])

    post = style_builder(line1, connector, line2, opener)

    # تنظيف أخير
    post = clean_text(post)

    # ضمان عدم الطول الزائد
    lines = [x.strip() for x in post.split("\n") if x.strip()]
    if len(lines) > 2:
        lines = lines[:2]
        post = "\n".join(lines)

    return clean_text(post)


def get_unique_post(max_attempts: int = 300) -> str:
    for _ in range(max_attempts):
        post = build_post_once()
        key = post.lower().strip()

        if key not in USED_POSTS:
            USED_POSTS.add(key)
            return post

    # fallback
    post = build_post_once()
    USED_POSTS.add(post.lower().strip())
    return post


def build_keyboard(post_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Generate Post 🔥", callback_data="generate_post")],
            [InlineKeyboardButton("Copy Post 📋", copy_text=CopyTextButton(text=post_text))],
        ]
    )


# =========================
# TELEGRAM HANDLERS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

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
    if update.message is None:
        return

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
    if update.message is None:
        return

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


# =========================
# MAIN
# =========================

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
