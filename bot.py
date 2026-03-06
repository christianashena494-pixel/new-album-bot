import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ⚠️ CHANGE THESE FOR EACH BOT
BOT_TOKEN = "8783390241:AAEyAeFVUW0bWKOKIzljWuRSFsbTTqk4gtE"
ADMIN_CHAT_ID = 685402824

logging.basicConfig(level=logging.INFO)


# -------------------------------
# START COMMAND
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 እንኳን ወደ አልበም መግዣ ቦት በደህና መጡ!\n\n"
        "🎵 Album: ልከተል\n"
        "💿 Tracks: 5 Songs\n"
        "💰 Price: 200 ETB\n\n"
        "📥 አልበሙን ለመግዛት 'Buy Album' ይጫኑ።"
    )

    keyboard = [
        [InlineKeyboardButton("🎧 Buy Album", callback_data="buy")],
        [InlineKeyboardButton("💳 Payment Options", callback_data="payment")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# -------------------------------
# BUY BUTTON
# -------------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        context.user_data["awaiting_payment"] = True

        instructions = (
            "💳 የክፍያ መመሪያ\n\n"
            "Send 200 ETB using one of these methods:\n\n"
            "📱 Telebirr\n"
            "📱 CBE Birr\n"
            "📱 Amole\n"
            "🏦 Bank Transfer\n\n"
            "📤 After payment send the transaction screenshot here."
        )

        await query.edit_message_text(instructions)


# -------------------------------
# PAYMENT OPTIONS BUTTON
# -------------------------------
async def payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "💳 Available Payment Methods\n\n"
        "📱 Mobile Money\n"
        "• Telebirr\n"
        "• CBE Birr\n"
        "• Amole\n\n"
        "🏦 Bank Transfer\n"
        "• Commercial Bank of Ethiopia\n"
        "• Awash Bank\n\n"
        "📤 After payment send screenshot here."
    )

    await query.edit_message_text(text)


# -------------------------------
# HELP BUTTON
# -------------------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "ℹ️ How to Buy Album\n\n"
        "1️⃣ Click Buy Album\n"
        "2️⃣ Send payment\n"
        "3️⃣ Upload payment screenshot\n"
        "4️⃣ Admin verifies payment\n"
        "5️⃣ Album will be delivered automatically 🎵"
    )

    await query.edit_message_text(text)


# -------------------------------
# HANDLE PAYMENT SCREENSHOT
# -------------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_payment"):
        return

    photo = update.message.photo[-1]
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    username = update.effective_user.username

    caption = (
        f"📩 New Payment Receipt\n\n"
        f"👤 Name: {full_name}\n"
        f"📛 Username: @{username}\n"
        f"🆔 User ID: {user_id}"
    )

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    ]]

    # Send screenshot to admin
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Notify user that payment was received
    await update.message.reply_text(
        "✅ Payment received! Admin will verify shortly."
    )

    context.user_data["awaiting_payment"] = False

# REJECT BUTTON HANDLER
# -------------------------------
async def reject_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("reject_"):
        return

    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("Unauthorized", show_alert=True)
        return

    user_id = int(query.data.split("_")[1])

    # Notify buyer
    await context.bot.send_message(
        chat_id=user_id,
        text="❌ ክፍያው አልተረጋገጠም።\n\nPlease check the payment and send screenshot again."
    )

    # Update admin message
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ Payment Rejected"
    )


# -------------------------------
# ADMIN APPROVE BUTTON HANDLER
# -------------------------------
async def approve_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Make sure this is an approve button
    if not query.data.startswith("approve_"):
        return

    # Only admin can approve
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("Unauthorized", show_alert=True)
        return

    # Get the user ID to send the album
    user_id = int(query.data.split("_")[1])

    # Notify the user
    await context.bot.send_message(
        chat_id=user_id,
        text="🎉 Payment Approved!\nSending your album..."
    )

    # List of MP3 file IDs (replace with your real ones)
    album_files = [
        "CQACAgIAAxkBAAMHaahcuDgZZP4c169hnYWd-kxFSw0AAl1NAAKX1PBKniqTiELGcaE6BA",
        "CQACAgIAAxkBAAMIaahcuLKblcUjwfTJymU_Rcmb0nAAAhczAAJO8LhIVAtolbUyn9M6BA",
        "CQACAgIAAxkBAAMJaahcuFf_PITqR5SAL4ob4gk7rtsAAi1TAAJ0SGFJg5A4emiQoeA6BA",
        "CQACAgIAAxkBAAMKaahcuLQCAVgLhDZ8QPrU6Ou-FK0AAhYjAAKHYzBILY2I2Mlj0Sg6BA",
        "CQACAgIAAxkBAAMLaahcuH4OpOYTmPLdBALGeMAyTPMAAoKFAAJATBhLMhkNy_fFC7Y6BA",
        # Add all tracks here
    ]

    # Send each track with download/forward protection enabled
    for file_id in album_files:
        await context.bot.send_audio(
            chat_id=user_id,
            audio=file_id,
            protect_content=True   # ✅ Prevents downloading & forwarding
        )

    # Thank you message
    await context.bot.send_message(
        chat_id=user_id,
        text="🙏 እናመሰግናለን!\nThank you for supporting the music."
    )

    # Update admin message to show approved
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ Approved & Album Sent"
    )


# -------------------------------
# TEMPORARY MP3 FILE ID GETTER (for debugging)
# -------------------------------
async def print_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.audio:
        print("FILE_ID:", update.message.audio.file_id)
        await update.message.reply_text("File ID printed in terminal!")


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(payment_options, pattern="^payment$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(approve_button, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(reject_button, pattern="^reject_"))
    app.add_handler(MessageHandler(filters.AUDIO, print_file_id))  # optional debug

    app.run_polling()


if __name__ == "__main__":
    main()
