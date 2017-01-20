#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This Bot uses the Updater class to handle the bot.
you can config it to watch processes on system
"""

from optparse import OptionParser
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import datetime
from pprint import pprint
__author__ = 'sekely'

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


class Bot(object):

    users = {}
    expenses = {}

    def __init__(self, token):
        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(token)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("register", self.register))
        dp.add_handler(CommandHandler("get", self.get))
        dp.add_handler(CommandHandler("debug", self.debug))
        dp.add_handler(CommandHandler("expanses", self.expanses))
        dp.add_handler(MessageHandler(Filters.text, self.handle_message))

        # log all errors
        dp.add_error_handler(self.error)

    def start_bot(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()



    def register(self, bot, update):
        chat_id = update.message.chat_id
        user = ' '.join(update.message.text.split()[1:])
        if user in self.expenses:
            update.message.reply_text('user already exists')
            return
        self.users[chat_id] = user
        self.expenses[user] = []
        update.message.reply_text('registered %s' % user)

    def get_user(self, update):
        print(update.message.chat_id)
        return self.users.get(update.message.chat_id, None)

    def _parse_text(self, txt):
        body = None
        exp = None
        if str.isnumeric(txt[-1]):
            exp = float(txt[-1])
            body = ' '.join(txt[:-1])
        if str.isnumeric(txt[0]):
            exp = float(txt[0])
            body = ' '.join(txt[1:])
        return exp, body

    def _create_entry(self, user, txt):
        exp, body = self._parse_text(txt)
        if not body or not exp:
            return
        now = str(datetime.date.today())
        self.expenses[user].append([now, user, exp, body])

    def handle_message(self, bot, update):
        print('serving')
        user = self.get_user(update)
        txt = update.message.text.split()
        self._create_entry(user, txt)

    def get(self, bot, update):
        update.message.reply_text(str(self.expenses[self.get_user(update)]))

    def debug(self, bot, update):
        pprint(self.users)
        pprint(self.expenses)

    def error(self, bot, update, error):
        pprint('Update "%s" caused error "%s"' % (update, error))


def get_parser():
    parser = OptionParser()
    parser.add_option('-t', '--token', dest='token', help='bot token')
    return parser.parse_args()


def main():
    print('starting expenses bot')
    options, _ = get_parser()
    bot = Bot(options.token)
    bot.start_bot()

if __name__ == '__main__':
    main()
