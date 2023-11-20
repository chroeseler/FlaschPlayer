#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import dataclasses
import logging
import os
from pathlib import Path

from ffmpy import FFmpeg
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

import text_queue as txt
import thequeue as q
from config import main_options as Options, Constants

GIF_COUNTER = 0

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Access:
    admin: int = int(os.environ['TELEGRAM_ADMIN'])
    users: list[int, ...] = dataclasses.field(default_factory=lambda: [])


USER_ACCESS = Access()
FUNCTIONS, ACCESS_ADD, ACCESS_REMOVE = range(3)


def got_access(user_id: int) -> bool:
    return user_id == USER_ACCESS.admin or user_id in USER_ACCESS.users

def update_access(user_id: int, remove: bool = False) -> None:
    if not remove:
        USER_ACCESS.users.append(user_id)
    else:
        USER_ACCESS.users.remove(user_id)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not got_access(update.message.from_user.id):
        await update.message.reply_text('Sorry, you do not have access to this functions, but I\'ll ask if it\'s cool that you do.')
        await context.bot.send_message(USER_ACCESS.admin, f'{update.message.from_user.first_name} {update.message.from_user.last_name} tried to access admin functions')
        await context.bot.send_message(USER_ACCESS.admin, f'{update.message.from_user.username}')
        await context.bot.send_message(USER_ACCESS.admin, f'{update.message.from_user.id}')
        return

    reply_keyboard = [['Add Access', "Remove Access", "Settings"]]

    await update.message.reply_text(
        'What can I do for you?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return FUNCTIONS


async def add_access_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please give the user id to be added.')
    return ACCESS_ADD


async def remove_access_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please give the user id to be removed.')
    return ACCESS_REMOVE


async def add_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update_access(update.message.id, remove=False)
    return ConversationHandler.END


async def remove_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update_access(update.message.id, remove=True)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def text_speed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /text_speed is issued."""
    if context.args and isinstance(int(context.args[0]), int):
        Options.text_speed = int(context.args[0])
        await update.message.reply_text(f"Text speed set to {context.args[0]}")
    else:
        await update.message.reply_text(f"Text speed can only be a round number. Default is 70 e.g. /text_speed 70")


async def brightness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /brightness is issued."""
    if context.args:
        brightness = float(context.args[0]) / 100
        Options.brightness = brightness
        await update.message.reply_text(f"Brightness set to {context.args[0]} : {brightness}")
    else:
        await update.message.reply_text(f"What percent of brightness do you want dear? E.g. /brightness 40")


async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /mood is issued."""
    Options.mood.set(context.args[0])
    Options.playlistmode.set("mood")
    await update.message.reply_text(f"Mood set {context.args[0]}")


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /mood is issued."""
    if context.args:
        Options.pattern.set(context.args[0])
        Options.playlistmode.set("pattern")
        await update.message.reply_text(f"Playing anything matching {context.args[0]} — note that it may not match anything")
    else:
        await update.message.reply_text("You need to provide something to select GIFs from our catalogue")


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Writing text on top of what is playing if issued with the /text command"""
    if len(update.message.text) > 120:
        await update.message.reply_text("Sorry that's quite the text and I'm a little lazy. Can you make it shorter?")
    else:
        txt.put(update.message.text)


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Path(f'{Constants.work_dir}/config/skip').touch()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logger.info(f'Starting Echo Handler')
    # update.message.reply_text(update.message.text)
    await update.message.reply_text("""Sorry this is not a gif or a picture and
I have no clue how to write text to that display thing there.
I mean have you seen how that works? It's fucking nuts.
I don't even know how to make letters that small and
I'm just an everyday bot. \n\n
Anyways, wanna give me a gif or a picture so I can resize it
to 25x12 pixel and show you? :D""")


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""Sorry this is not a gif or a picture and
I have no clue how to write text to that display thing there.
I mean have you seen how that works? It's fucking nuts.
I don't even know how to make letters that small and
I'm just an everyday bot. \n\n
Anyways, wanna give me a gif or a picture so I can resize it
to 25x12 pixel and show you? :D""")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.exception('Update "%s" caused error "%s"', update, context.error)


async def gif_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Starting Gif Handler')
    if update.message.document.file_size < 20000000:
        mp4 = context.bot.getFile(update.message.document.file_id)
        mp4.download(f'{Constants.work_dir}/media.mp4')
        logger.info(os.path.getsize(f'{Constants.work_dir}/media.mp4'))
        put_gifs(f'{Constants.work_dir}/media.mp4')
    else:
        await update.message.reply_text("""Wow! Sry that's way to big!
                I'm just a little pi and I can't handle that much traffic.
                Please send me something smaller. :)""")


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Starting Image Handler')
    pic = context.bot.getFile(update.message.photo[-1].file_id)
    pic.download(f'{Constants.work_dir}/photo.gif')
    put_gifs(f'{Constants.work_dir}/photo.gif')


def put_gifs(telegram_file) -> None:
    global GIF_COUNTER
    out = f'{Constants.work_dir}/gifs/{GIF_COUNTER:06d}.gif'
    try:
        ff = FFmpeg(
            inputs={telegram_file: '-y -hide_banner -loglevel error'},  # TODO Remove the -y ??/
            outputs={out: '-s 20x15'})
        ff.run()
        try:
            with open(out) as f:
                logger.info(f'Gif creation successful: {out}')
        except IOError:
            logger.warning(f'Gif creation failed: {out}')
    except Exception as e:
        logger.exception('FFmpeg Error!')
    try:
        q.mark_ready(out)
        GIF_COUNTER += 1
    except Exception as e:
        logger.exception('Catched unregular exception: %s', e)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ['BOT_TOKEN']
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    #application.add_handler(CommandHandler("start", admin))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("brightness", brightness))
    application.add_handler(CommandHandler("text_speed", text_speed))
    application.add_handler(CommandHandler("mood", mood))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("skip", skip))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.PHOTO, image_handler))
    application.add_handler(MessageHandler(filters.VIDEO, gif_handler))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # conversion to add or remove user
    conv_handler = ConversationHandler(

        entry_points=[CommandHandler("start", admin)],

        states={
            #"Access", "Settings"
            FUNCTIONS: [
                MessageHandler(filters.Regex("^Add Access$"), add_access_input),
                MessageHandler(filters.Regex("^Remove Access$"), remove_access_input),
                #MessageHandler(filters.Regex("^Settings$"), other_function)
            ],
            #MessageHandler(Filters.text & ~Filters.command, receive_input)
            ACCESS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_access)],
            ACCESS_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_access)],
        },

        fallbacks=[CommandHandler("cancel", cancel)],

    )


    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()