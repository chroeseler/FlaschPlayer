#!/usr/bin/ python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
import sys
import threading
import traceback
from pathlib import Path
from signal import SIGINT, signal

from ffmpy import FFmpeg
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import text_queue as txt
import thequeue as q
from config import Constants, main_options as Options

GIF_COUNTER = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.bot")


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.effective_chat.send_message('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.effective_chat.send_message('Help!')


def text_speed(update, context):
    """Send a message when the command /text_speed is issued."""
    if context.args and isinstance(int(context.args[0]), int):
        Options.text_speed = int(context.args[0])
        update.effective_chat.send_message(f"Text speed set to {context.args[0]}")
    else:
        update.effective_chat.send_message(f"Text speed can only be a round number. Default is 70 e.g. /text_speed 70")


def brightness(update, context):
    """Send a message when the command /brightness is issued."""
    if context.args:
        brightness = float(context.args[0]) / 100
        Options.brightness = brightness
        #update.effective_chat.send_message(f"Brightness set to {context.args[0]} : {brightness}")
        update.effective_chat.send_message(f"Brightness set to {context.args[0]} : {brightness}")
    else:
        update.effective_chat.send_message(f"What percent of brightness do you want dear? E.g. /brightness 40")


def mood(update, context):
    """Send a message when the command /mood is issued."""
    Options.mood.set(context.args[0])
    Options.playlistmode.set("mood")
    update.effective_chat.send_message(f"Mood set {context.args[0]}")


def play(update, context):
    """Send a message when the command /mood is issued."""
    if context.args:
        Options.pattern.set(context.args[0])
        Options.playlistmode.set("pattern")
        update.effective_chat.send_message(f"Playing anything matching {context.args[0]} — note that it may not match anything")
    else:
        update.effective_chat.send_message("You need to provide something to select GIFs from our catalogue")


def text(update, context):
    """Writing text on top of what is playing if issued with the /text command"""
    if len(update.message.text) > 120:
        update.effective_chat.send_message("Sorry that's quite the text and I'm a little lazy. Can you make it shorter?")
    else:
        txt.put(update.message.text)


def skip(update, context):
    Path(f'{Constants.work_dir}/config/skip').touch()


def echo(update, context):
    """Echo the user message."""
    logger.info(f'Starting Echo Handler')
    # update.effective_chat.send_message(update.message.text)
    update.effective_chat.send_message("""Sorry this is not a gif or a picture and
I have no clue how to write text to that display thing there.
I mean have you seen how that works? It's fucking nuts.
I don't even know how to make letters that small and
I'm just an everyday bot. \n\n
Anyways, wanna give me a gif or a picture so I can resize it
to 20x15 pixel and show you? :D""")


def voice_handler(update, context):
    update.effective_chat.send_message("""Sorry this is not a gif or a picture and
I have no clue how to write text to that display thing there.
I mean have you seen how that works? It's fucking nuts.
I don't even know how to make letters that small and
I'm just an everyday bot. \n\n
Anyways, wanna give me a gif or a picture so I can resize it
to 20x15 pixel and show you? :D""")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    error = traceback.format_exc()
    logger.error(f"Error: {str(context.error)}\n{error}")




def gif_handler(update, context):
    logger.info(f'Starting Gif Handler')
    if update.message.document.file_size < 20000000:
        mp4 = context.bot.getFile(update.message.document.file_id)
        mp4.download(f'{Constants.work_dir}/media.mp4')
        logger.info(os.path.getsize(f'{Constants.work_dir}/media.mp4'))
        put_gifs(f'{Constants.work_dir}/media.mp4')
    else:
        update.effective_chat.send_message("""Wow! Sry that's way to big!
                I'm just a little pi and I can't handle that much traffic.
                Please send me something smaller. :)""")


def image_handler(update, context):
    logger.info(f'Starting Image Handler')
    pic = context.bot.getFile(update.message.photo[-1].file_id)
    pic.download(f'{Constants.work_dir}/photo.gif')
    put_gifs(f'{Constants.work_dir}/photo.gif')


def put_gifs(telegram_file):
    global GIF_COUNTER
    out = f'{Constants.work_dir}/gifs/{GIF_COUNTER:06d}.gif'
    try:
        ff = FFmpeg(
            inputs={telegram_file: '-y -hide_banner -loglevel error'},  # TODO Remove the -y ??/
            outputs={out: '-s 25x12'})
        ff.run()
        try:
            with open(out) as f:
                logger.info(f'Gif creation successful: {out}')
        except IOError:
            logger.exception(f'Gif creation failed: {out}')
    except Exception as e:
        logger.exception('FFmpeg Error!')
    try:
        q.mark_ready(out)
        GIF_COUNTER += 1
    except Exception as e:
        logger.error(traceback.format_exec())


def make_updater():
    token = os.environ['BOT_TOKEN']
    logger.info(f'Token: {token}')

    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("brightness", brightness))
    dp.add_handler(CommandHandler("text_speed", text_speed))
    dp.add_handler(CommandHandler("mood", mood))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(CommandHandler("skip", skip))

    dp.add_handler(MessageHandler(Filters.voice, voice_handler))
    dp.add_handler(MessageHandler(Filters.photo, image_handler))
    dp.add_handler(MessageHandler(Filters.document.mime_type("video/mp4"), gif_handler))

    # on command i.e. message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text))

    # log all errors
    dp.add_error_handler(error)

    return updater


stopped = False


class System:
    def __init__(self):
        """Start the bot."""
        # Create the Updater and pass it your bots token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        logger.info('##########################   bot  #########')
        logger.info("Setting up queues")
        q.setup()
        txt.setup()
        self.updater = make_updater()

    def start(self):
        self.updater.start_polling()

    def stop(self):
        global stopped
        if not stopped:
            stopped = 1
            self.updater.stop()  # this function can take seconds!
            self.updater.idle()
        else:
            logger.info("Stop already initiated")


def main(pill: threading.Event = threading.Event()) -> None:
    s = System()
    s.start()
    pill.wait()
    s.stop()


if __name__ == '__main__':
    s = System()


    def handler(signal_received, frame):
        # Handle any cleanup here
        logger.info('SIGINT or CTRL-C detected. Exiting gracefully')
        s.stop()
        sys.exit(0)


    signal(SIGINT, handler)

    print('Running. Press CTRL-C to exit.')
    s.start()
