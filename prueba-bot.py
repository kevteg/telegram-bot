#!/usr/bin/env python
#
# Simple Bot to reply Telegram messages
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].


import logging
import telegram
import urllib
import random
import foto

LAST_UPDATE_ID = None


def main():
    global LAST_UPDATE_ID

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Telegram Bot Authorization Token
    bot = telegram.Bot('53133786:AAE-aoWp6wwlfS0DOm52QYs6s0PR8jwV8QA')

    # This will be our global variable to keep the latest update_id when requesting
    # for updates. It starts with the latest update_id if available.
    try:
        print bot.getMe()
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    while True:
        echo(bot)


def echo(bot):
    global LAST_UPDATE_ID

    # Request updates after the last updated_id
    for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
        # chat_id is required to reply any message
        chat_id = update.message.chat_id
        message = update.message.text.encode('utf-8')
        nombre  = update.message.from_user.username
	persona = update.message.from_user.first_name

        if (message):
            print nombre + ": " + message
            if message == "/start":
                bot.sendMessage(chat_id=chat_id,
                                text="Hola @"+nombre+", @keeeevin es mi padre")
                bot.sendMessage(chat_id=chat_id,
                                text="Estoy aqui para hablar")
            # Reply the message
            if message == "/foto" or message == "/foto@lprotobot":
		foto.toma()
		bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
		bot.sendPhoto(chat_id=chat_id, photo=open('Foto.png', 'r'))
            else:
                #
		bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                bot.sendMessage(chat_id=chat_id,
                                text=ed(message))

            # Updates global offset to get the new updates
            LAST_UPDATE_ID = update.update_id + 1
def ed(text):
    res = ["Si", "No", "Depende", "Gerardo desaparecio", "I'm sorry Dave, I'm afraid I can't do that", "robots", "Whatsapp sucks", "I am cool", "Kevin es cul", "Chabe vive", "Bate para Jesus"];
    data = res[random.randint(1, len(res) - 1)];

    return data.strip()

if __name__ == '__main__':
    main()
