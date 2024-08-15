# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# apt-get install python3-python-telegram-bot
import logging

from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


class MyTelegram:
    """Access to a telegram bot"""

    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        update.message.reply_markdown_v2(
            rf"Hi {user.mention_markdown_v2()}\!",
            reply_markup=ForceReply(selective=True),
        )

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        update.message.reply_text("Help!")

    def echo(self, update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    def __init__(self, token):
        updater = Updater(token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help_command))
        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.echo)
        )
        updater.start_polling()
        updater.idle()
