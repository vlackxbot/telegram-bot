import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # e.g., https://your-app.onrender.com

CHANNELS = ['@marcoshots', '@marcoshotpot', '@earnyvlackyo', '@giftcodedaily100', '@jiyajishots', '@aarohiloots']
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    with open('front.png', 'rb') as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption="👋 Welcome! Join all channels below to get ₹100 Paytm cash.")

    with open('voice.ogg', 'rb') as voice:
        await context.bot.send_voice(chat_id=chat_id, voice=voice)

    buttons = [
        [InlineKeyboardButton("Join ↗️", url="https://t.me/marcoshots"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/marcoshotpot"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/earnyvlackyo")],
        [InlineKeyboardButton("Join ↗️", url="https://t.me/giftcodedaily100"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/jiyajishots"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/aarohiloots")],
        [InlineKeyboardButton("✅ VERIFY ✅", callback_data="verify")]
    ]

    await context.bot.send_message(chat_id=chat_id,
                                   text="Please join all the above channels and then click 'I've Joined All'.",
                                   reply_markup=InlineKeyboardMarkup(buttons))

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    not_joined = []

    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)

    if not_joined:
        await query.answer("Please join all channels before verifying.", show_alert=True)
        return

    await query.answer("✅ Verified successfully!", show_alert=False)
    await context.bot.send_message(chat_id=chat_id, text="✅ Verification successful!")

    with open("wheel.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption="🎯 Spin the wheel to win up to ₹100 Paytm cash!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 Spin Now", callback_data="spin")]
            ])
        )

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    await query.answer("Spinning the wheel...")

    amounts = [33, 55]
    won_amount = random.choice(amounts)
    user_data[user.id] = {'balance': won_amount, 'referrals': 0, 'upi': None}

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎉 Congratulations! You won ₹{won_amount}.\n\nMinimum withdrawal is ₹100. Refer friends to earn more.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]
        ])
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    user_info = user_data.get(user.id, {'balance': 0, 'referrals': 0})

    if user_info['balance'] >= 100:
        await context.bot.send_message(chat_id=chat_id, text="Please enter your UPI ID for withdrawal.")
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Your current balance is ₹{user_info['balance']}.\nRefer more friends.",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]
                                       ]))

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    link = f"https://t.me/GETUPIINSTANTBOT?start={user.id}"
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"Share this link: {link}\nYou'll earn ₹10 for each referral.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    if "@" in text or "." in text:
        user_info = user_data.get(user.id)
        if user_info and user_info['balance'] >= 100:
            user_info['upi'] = text
            await context.bot.send_message(chat_id=chat_id,
                                           text="✅ Your UPI ID received. ₹100 will be sent within 24 hrs.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="You need ₹100 to withdraw.")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    application.add_handler(CallbackQueryHandler(spin, pattern="^spin$"))
    application.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    application.add_handler(CallbackQueryHandler(refer, pattern="^refer$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set webhook
    await application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_path=f"/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
