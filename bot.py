import os
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaAudio,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Replace with your actual bot token
BOT_TOKEN = "8148462890:AAGwW8GFMhQSzbSUO2CQHQ7VOX9ORc3dv4U"

# List of your channel usernames
CHANNELS = ['@marcoshots', '@marcoshotpot', '@earnyvlackyo', '@giftcodedaily100', '@jiyajishots', '@aarohiloots']

# Dictionary to store user data
user_data = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Send welcome image with caption
    with open('front.png', 'rb') as photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption="👋 Welcome! Join all channels below to get ₹100 Paytm cash."
        )

    # Send voice note
    with open('voice.ogg', 'rb') as voice:
        await context.bot.send_voice(chat_id=chat_id, voice=voice)

    # Create channel join buttons
    buttons = [
         [InlineKeyboardButton("Join ↗️", url="https://t.me/@marcoshots"), InlineKeyboardButton("Join ↗️", url="https://t.me/@marcoshotpot"), InlineKeyboardButton("Join ↗️", url="https://t.me/@earnyvlackyo")],
    [InlineKeyboardButton("Join ↗️", url="https://t.me/@giftcodedaily100"), InlineKeyboardButton("Join ↗️", url="https://t.me/@jiyajishots"), InlineKeyboardButton("Join ↗️", url="https://t.me/@aarohiloots")],
    [InlineKeyboardButton("✅ VERIFY ✅", callback_data="verify")]
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text="Please join all the above channels and then click 'I've Joined All'.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ Verification handler
# ✅ Verification handler
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    not_joined = []

    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)

    if not_joined:
        await query.answer("Please join all channels before verifying.", show_alert=True)
        return

    await query.answer("✅ Verified successfully!", show_alert=False)
    await context.bot.send_message(chat_id=chat_id, text="✅ Verification successful!")

    # Send lucky wheel image and button
    with open("wheel.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
             caption="🎯 Spin the wheel to win up to ₹100 Paytm cash!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 Spin Now", callback_data="spin")]
            ])
        )



# Spin handler
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    # Simulate spinning
    await query.answer("Spinning the wheel...")

    # Pred4etermined amounts
    amounts = [33, 55]
    won_amount = random.choice(amounts)

    # Store user's won amount
    user_data[user.id] = {
        'balance': won_amount,
        'referrals': 0,
        'upi': None
    }

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎉 Congratulations! You won ₹{won_amount}.\n\nMinimum withdrawal is ₹100. Refer friends to earn more.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]
        ])
    )

# Withdraw handler
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    user_info = user_data.get(user.id, {'balance': 0, 'referrals': 0})

    if user_info['balance'] >= 100:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter your UPI ID for withdrawal."
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Your current balance is ₹{user_info['balance']}.\nRefer more friends to reach ₹100.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]
        ])
    )

# Referral handler
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    referral_link = f"https://t.me/GETUPIINSTANTBOT?start={user.id}"

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Share this link with your friends: {referral_link}\nYou'll earn ₹10 for each referral."
    )

# Message handler for UPI ID submission
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    if "@" in text or "." in text:
        user_info = user_data.get(user.id)
        if user_info and user_info['balance'] >= 100:
            user_info['upi'] = text
            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ Your UPI ID has been received. You'll receive ₹100 within 24 hours."
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You need a minimum balance of ₹100 to withdraw."
            )

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(spin, pattern="^spin$"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    app.add_handler(CallbackQueryHandler(refer, pattern="^refer$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
