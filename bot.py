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
import csv
from bidi import algorithm as bidialg

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

    def __init__(self, token):
        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(token)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("register", self.register))
        dp.add_handler(CommandHandler("debug", self.debug))
        dp.add_handler(CommandHandler("rename", self.rename))
        dp.add_handler(MessageHandler(Filters.text, self.handle_message))

        # log all errors
        dp.add_error_handler(self.error)

    def start_bot(self):
        self._save_to_file(['date', 'user', 'price', 'details'])
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()



    def register(self, bot, update):
        chat_id = update.message.chat_id
        user = ' '.join(update.message.text.split()[1:])
        if user in self.users.values():
            update.message.reply_text('user already exists')
            return
        self.users[chat_id] = user
        update.message.reply_text('registered %s' % user)

    def rename(self, bot, update):
        chat_id = update.message.chat_id
        user = ' '.join(update.message.text.split()[1:])
        self.users.pop(chat_id)
        self.users[chat_id] = user

    def get_user(self, update):
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
        if body:
            body = bidialg.get_display(body)
        return exp, body

    def _create_entry(self, user, txt):
        exp, body = self._parse_text(txt)
        if not body or not exp:
            return
        now = str(datetime.date.today())
        entry = [now, user, exp, body]
        return entry

    def _save_to_file(self, row=[]):
        with open('expenses.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(row)


    def handle_message(self, bot, update):
        user = self.get_user(update)
        txt = update.message.text.split()
        entry = self._create_entry(user, txt)
        if entry:
            self._save_to_file(entry)


    def debug(self, bot, update):
        pprint(self.users)

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
