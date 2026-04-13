import asyncio
import re
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# =========================================
# ضع هنا توكن البوت من BotFather
# =========================================
BOT_TOKEN = "8270434304:AAEvqdkWyn7pOGTGIGanUXiP_zirNfFoZjM"

# =========================================
# Spin Text
# السطر الأول = افتتاحية
# السطر الثاني = النتيجة / الملاحظة
# =========================================
LINE1_SPIN = r"""
({I wasn’t even looking for this|I almost skipped checking today|Didn’t expect anything new today|Was just scrolling for a second|Opened the app randomly|I was only checking for a moment|Didn’t plan to look again today|I wasn’t expecting anything different|I almost ignored this completely|Was just passing by quickly}
{ |…|}
)
"""

LINE2_SPIN = r"""
({but something new showed up while scrolling|and something unexpected appeared|and I noticed a small change|but something felt different this time|and I saw something I didn’t expect|but something caught my attention|and a small update appeared|but I ended up noticing something new|and there was a change I didn’t expect|but something unusual popped up}
)
"""

# قائمة الإيموجي
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

    # إضافة إيموجي في أغلب الحالات
    if random.random() < 0.85:
        if not any(emoji in line2 for emoji in EMOJIS):
            line2 += " " + random.choice(EMOJIS)

    post = f"{line1}\n{line2}"
    return clean_text(post)


# =========================================
# أوامر تيليجرام
# =========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (
        "Bot is running.\n\n"
        "Commands:\n"
        "/post - generate one post\n"
        "/help - show help"
    )
    await update.message.reply_text(msg)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (
        "Available commands:\n"
        "/post - generate one post\n"
        "/start - start the bot\n"
        "/help - show help"
    )
    await update.message.reply_text(msg)


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = generate_single_post()
    await update.message.reply_text(post)


def main() -> None:
    # مهم لبعض إصدارات بايثون الحديثة
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post_command))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()