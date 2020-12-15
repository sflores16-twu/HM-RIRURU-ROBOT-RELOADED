
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot, ParseMode
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from SaitamaRobot import dispatcher
from SaitamaRobot.modules.helper_funcs.chat_status import user_not_admin, user_admin, can_delete
from SaitamaRobot.modules.helper_funcs.extraction import extract_text
from SaitamaRobot.modules.sql import antiarabic_sql as sql

ANTIARABIC_GROUPS = 12


@run_async
@user_admin
def antiarabic_setting(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    member = chat.get_member(int(user.id))

    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            if args[0].lower() in ("yes", "on", "true"):
                sql.set_chat_setting(chat.id, True)
                msg.reply_text("Turned on AntiArabic! Messages sent by any non-admin which contains arabic text will be deleted.")

            elif args[0].lower() in ("no", "off", "false"):
                sql.set_chat_setting(chat.id, False)
                msg.reply_text("Turned off AntiArabic! Messages containing arabic text won't be deleted.")
    
        
       
ANTIARABIC_HELP = f"""
*Here is the help for the Anti Arabic module:*

AntiArabicScript module is used to delete messages containing characters from one of the following automatically:

• Arabic
• Arabic Supplement
• Arabic Extended-A
• Arabic Presentation Forms-A
• Arabic Presentation Forms-B
• Rumi Numeral Symbols
• Arabic Mathematical Alphabetic Symbol

*NOTE:* AntiArabicScript module doesn't affect messages sent by admins.

_Admin only:_
 ◉ `/antiarabic <on/off>`: turn antiarabic module on/off ( off by default )
 """


def antiarabic_help_sender(update: Update):
    update.effective_message.reply_text(
        ANTIARABIC_HELP, parse_mode=ParseMode.HTML)
    
@run_async
def antiarabic_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            'Contact me in pm',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "AntiArabic help",
                    url=f"t.me/{context.bot.username}?start=antiarabic")
            ]]))
        return
    antiarabic_help_sender(update)
    
    
@user_not_admin
@run_async
def antiarabic(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    msg = update.effective_message
    to_match = extract_text(msg)
    user = update.effective_user
    has_arabic = False

    if not sql.chat_antiarabic(chat.id):
        return ""

    if not user:  # ignore channels
        return ""

    if user.id == 777000:  # ignore telegram
        return ""

    if not to_match:
        return

    if chat.type != chat.PRIVATE:
        for c in to_match:
            if ('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F'
                    or '\u08A0' <= c <= '\u08FF' or '\uFB50' <= c <= '\uFDFF'
                    or '\uFE70' <= c <= '\uFEFF'
                    or '\U00010E60' <= c <= '\U00010E7F'
                    or '\U0001EE00' <= c <= '\U0001EEFF'):
                if can_delete(chat, bot.id):
                    update.effective_message.delete()
                    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)







SETTING_HANDLER = CommandHandler("antiarabic", antiarabic_setting,
                                 pass_args=True)
ANTIARABIC = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo) & Filters.group, antiarabic)
ANTIARABIC_HELP_HANDLER = CommandHandler("antiarabichelp", antiarabic_help)

dispatcher.add_handler(SETTING_HANDLER)
dispatcher.add_handler(ANTIARABIC, group=ANTIARABIC_GROUPS)
dispatcher.add_handler(ANTIARABIC_HELP_HANDLER)
