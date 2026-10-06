from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download", callback_data="download"),
         InlineKeyboardButton("💎 Premium", callback_data="premium")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile"),
         InlineKeyboardButton("❓ Help", callback_data="help")]
    ])
