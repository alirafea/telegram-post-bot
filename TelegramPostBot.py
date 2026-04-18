import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

curiosity_templates = [
    [
        ["I noticed", "I saw", "I found", "A quick look showed", "I came across"],
        ["something new", "a small change", "something different", "an update", "something interesting"],
        ["today", "just now", "earlier", "recently"],
        ["See below", "Check the comments", "Look below", "Have a quick look"]
    ],
    [
        ["At first I almost missed it", "I wasn’t expecting this", "I checked for a second"],
        ["but something changed", "and found an update", "and noticed a difference"],
        ["Look below", "See the comments", "Take a look below"]
    ]
]

direct_templates = [
    [
        ["New update is live", "Latest update is here", "Fresh post is up", "Today’s update is ready"],
        ["Check below", "See the comments", "Take a look", "Look below now"]
    ],
    [
        ["There’s a new post now", "New content is available", "The latest one is up"],
        ["Look below", "Open the comments", "View the update below"]
    ]
]

normal_templates = [
    [
        ["New post today", "Fresh content today", "There’s something new", "A new update is available"],
        ["Have a look", "See below", "Take a quick look", "Check it out"]
    ],
    [
        ["Posted something new today", "Shared a new update", "Added a fresh post"],
        ["Take a look", "See below", "Look in the comments"]
    ]
]

last_opening = None
last_closing = None

def build_post(template_group):
    global last_opening, last_closing

    template = random.choice(template_group)
    parts = []

    for idx, choices in enumerate(template):
        pool = choices[:]
        random.shuffle(pool)

        if idx == 0 and last_opening in pool and len(pool) > 1:
            pool.remove(last_opening)

        if idx == len(template) - 1 and last_closing in pool and len(pool) > 1:
            pool.remove(last_closing)

        choice = random.choice(pool)
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

    return f"{line1}\n{line2}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["بوستات فضول", "بوستات مباشرة"], ["بوستات عادية"]]
    await update.message.reply_text(
        "اختر نوع البوست:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "بوستات فضول":
        post = build_post(curiosity_templates)
    elif text == "بوستات مباشرة":
        post = build_post(direct_templates)
    elif text == "بوستات عادية":
        post = build_post(normal_templates)
    else:
        post = "اكتب /start ثم اختر نوع البوست"

    await update.message.reply_text(post)

def main():
    app = ApplicationBuilder().token("BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
