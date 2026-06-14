#!/usr/bin/ python3
import asyncio
import logging
import os
import sys
import threading
import traceback
from pathlib import Path
from signal import SIGINT, signal

from ffmpy import FFmpeg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

import text_queue as txt
import thequeue as q
from config import Constants, Main_Options as Options

GIF_COUNTER = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.bot")


async def start(update, context):
    logger.info("Handler: /start from chat_id=%s", update.effective_chat.id)
    await update.effective_chat.send_message('Hi! Type /help to see what I can do.')


async def help(update, context):
    chat_id = update.effective_chat.id
    has_access = _has_access(chat_id)
    is_root = chat_id == Constants.root

    public_section = (
        "🎬 *Anyone can do:*\n"
        "  Send a text message → scrolls across the display (max 120 chars)\n"
        "  Send a photo or GIF → displayed on screen\n"
        "  Send a video (mp4) → converted and queued\n"
        "  /start — say hi\n"
        "  /help — this message\n"
    )

    if not has_access:
        await update.effective_chat.send_message(
            public_section + "\n_You don't have control access. Ask the admin to add you._",
            parse_mode='Markdown',
        )
        return

    from blinky import _discover_programs
    import os

    res_str = '25_12'
    backgrounds_root = os.path.join(Constants.work_dir, 'data', 'backgrounds', res_str)
    moods = sorted(
        d for d in os.listdir(backgrounds_root)
        if os.path.isdir(os.path.join(backgrounds_root, d))
    )
    programs = [p.split('.')[-1] for p in _discover_programs()]

    control_section = (
        "🎛 *Control commands:*\n"
        f"  /mood <name> — set mood playlist\n"
        f"    Moods: {', '.join(moods)}\n"
        f"  /play <keyword> — play GIFs matching a keyword\n"
        f"  /program [name] — switch to programmatic mode (cycles all if no name)\n"
        f"    Programs: {', '.join(programs)}\n"
        f"  /programs — list programs\n"
        f"  /skip — skip current GIF or program\n"
        f"  /brightness <0–100> — set brightness (e.g. /brightness 40)\n"
        f"  /text\\_speed <number> — scroll speed, default 70 (higher = slower)\n"
    )

    message = public_section + "\n" + control_section

    if is_root:
        root_section = (
            "\n👑 *Root-only commands:*\n"
            "  /addmaintainer — grant access (reply to their msg, forward their msg, or numeric ID)\n"
            "  /removemaintainer — revoke access\n"
            "  /listmaintainers — show all users with access\n"
            "  Share a contact → same as /addmaintainer (toggles access)\n"
        )
        message += root_section

    await update.effective_chat.send_message(message, parse_mode='Markdown')


async def text_speed(update, context):
    if not await check_access(update):
        return
    if context.args and isinstance(int(context.args[0]), int):
        Options.text_speed = int(context.args[0])
        await update.effective_chat.send_message(f"Text speed set to {context.args[0]}")
    else:
        await update.effective_chat.send_message(f"Text speed can only be a round number. Default is 70 e.g. /text_speed 70")


async def brightness(update, context):
    if not await check_access(update):
        return
    if context.args:
        b = float(context.args[0]) / 100
        Options.brightness = b
        await update.effective_chat.send_message(f"Brightness set to {context.args[0]} : {b}")
    else:
        await update.effective_chat.send_message(f"What percent of brightness do you want dear? E.g. /brightness 40")


async def mood(update, context):
    if not await check_access(update):
        return
    Options.mood = context.args[0]
    Options.playlistmode = "mood"
    await update.effective_chat.send_message(f"Mood set {context.args[0]}")


async def play(update, context):
    if not await check_access(update):
        return
    if context.args:
        Options.pattern = context.args[0]
        Options.playlistmode = "pattern"
        await update.effective_chat.send_message(f"Playing anything matching {context.args[0]} — note that it may not match anything")
    else:
        await update.effective_chat.send_message("You need to provide something to select GIFs from our catalogue")


async def program(update, context):
    if not await check_access(update):
        return
    from blinky import _discover_programs
    available = [p.split('.')[-1] for p in _discover_programs()]
    if context.args:
        name = context.args[0]
        if name not in available:
            await update.effective_chat.send_message(
                f"Unknown program '{name}'. Available: {', '.join(available)}"
            )
            return
        Options.program = name
        Options.playlistmode = 'programmatic'
        await update.effective_chat.send_message(f"Switched to programmatic mode: {name}")
    else:
        Options.program = ''
        Options.playlistmode = 'programmatic'
        await update.effective_chat.send_message(
            f"Switched to programmatic mode (cycling all):\n{', '.join(available)}"
        )


async def programs(update, context):
    if not await check_access(update):
        return
    from blinky import _discover_programs
    available = [p.split('.')[-1] for p in _discover_programs()]
    await update.effective_chat.send_message(
        "Available programs:\n" + "\n".join(f"• {p}" for p in available)
    )


async def text(update, context):
    logger.info("Handler: text from chat_id=%s: %s", update.effective_chat.id, update.effective_message.text[:40])
    if len(update.effective_message.text) > 120:
        await update.effective_chat.send_message("Sorry that's quite the text and I'm a little lazy. Can you make it shorter?")
    else:
        txt.put(update.effective_message.text)


async def skip(update, context):
    if not await check_access(update):
        return
    Path(f'{Constants.work_dir}/config_files/skip').touch()


async def voice_handler(update, context):
    await update.effective_chat.send_message("""Sorry this is not a gif or a picture and
I have no clue how to write text to that display thing there.
I mean have you seen how that works? It's fucking nuts.
I don't even know how to make letters that small and
I'm just an everyday bot. \n\n
Anyways, wanna give me a gif or a picture so I can resize it
to 20x15 pixel and show you? :D""")


async def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    err = traceback.format_exc()
    logger.error(f"Error: {str(context.error)}\n{err}")


async def gif_handler(update, context):
    logger.info(f'Starting Gif Handler')
    if update.effective_message.document.file_size < 20000000:
        mp4 = await context.bot.get_file(update.effective_message.document.file_id)
        await mp4.download_to_drive(f'{Constants.work_dir}/media.mp4')
        logger.info(os.path.getsize(f'{Constants.work_dir}/media.mp4'))
        put_gifs(f'{Constants.work_dir}/media.mp4')
    else:
        await update.effective_chat.send_message("""Wow! Sry that's way to big!
                I'm just a little pi and I can't handle that much traffic.
                Please send me something smaller. :)""")


async def image_handler(update, context):
    logger.info(f'Starting Image Handler')
    pic = await context.bot.get_file(update.effective_message.photo[-1].file_id)
    await pic.download_to_drive(f'{Constants.work_dir}/photo.gif')
    put_gifs(f'{Constants.work_dir}/photo.gif')


def put_gifs(telegram_file):
    global GIF_COUNTER
    out = f'{Constants.work_dir}/gifs/{GIF_COUNTER:06d}.gif'
    try:
        ff = FFmpeg(
            inputs={telegram_file: '-y -hide_banner -loglevel error'},
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
        logger.exception('Failure adding gif to queue')


async def access_handler(update, context):
    logger.info(f'Starting Access Handler')
    if update.effective_chat.id != Constants.root:
        await update.effective_chat.send_message("Access denied!")
    else:
        await update.effective_chat.send_message("Access granted.")
        telegram_id = update.effective_message.contact.user_id
        first = update.effective_message.contact.first_name
        last = update.effective_message.contact.last_name
        full_name = f'{first} {last}'.strip()
        if telegram_id not in Options.allowed_ids:
            Options.add_id(telegram_id, full_name)
            await update.effective_chat.send_message(f'Added {full_name} to access list')
        else:
            Options.remove_id(telegram_id)
            await update.effective_chat.send_message(f'Removed {full_name} from access list')


def _has_access(chat_id: int) -> bool:
    return chat_id in Options.allowed_ids


async def relay_to_root(update, context):
    """Forward every non-root message to root for monitoring."""
    if not update.effective_message or not update.effective_user:
        return
    if update.effective_chat.id == Constants.root:
        return

    sender = update.effective_user
    username = f" (@{sender.username})" if sender.username else ""
    label = f"📨 {sender.full_name}{username} [{sender.id}]:"

    try:
        await context.bot.send_message(Constants.root, label)
        await context.bot.forward_message(
            chat_id=Constants.root,
            from_chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )
    except Exception:
        logger.exception("Failed to relay message to root")


async def check_access(update) -> bool:
    if not _has_access(update.effective_chat.id):
        await update.effective_chat.send_message('Access denied!')
        return False
    return True


def _origin_user(msg):
    """Return (id, name) from a message's forward_origin, or None if not available."""
    origin = msg.forward_origin
    if origin is not None and hasattr(origin, 'sender_user') and origin.sender_user:
        u = origin.sender_user
        return u.id, u.full_name
    return None, None


def _resolve_user(update, context) -> tuple[int | None, str]:
    """Extract (user_id, display_name) from reply, forward, or numeric argument."""
    msg = update.effective_message

    # Method 1: reply to a message.
    # When root replies to a relayed-forward, the replied message has forward_origin
    # pointing to the original sender — check that first before from_user (which is the bot).
    if msg.reply_to_message:
        uid, name = _origin_user(msg.reply_to_message)
        if uid:
            return uid, name
        u = msg.reply_to_message.from_user
        if u and not u.is_bot:
            return u.id, u.full_name

    # Method 2: this message itself is a forward
    uid, name = _origin_user(msg)
    if uid:
        return uid, name

    # Method 3: numeric ID as argument
    if context.args:
        try:
            return int(context.args[0]), context.args[0]
        except ValueError:
            pass

    return None, ''


_MAINTAINER_USAGE = (
    "How to identify the user:\n"
    "• *Reply* to one of their messages with this command\n"
    "• *Forward* any message from them to me, then send this command\n"
    "  _(won't work if they hide forwarded identity in Telegram privacy settings)_\n"
    "• Pass their *numeric ID*: `/addmaintainer 123456789`\n"
    "  _(they can find it by messaging @userinfobot)_"
)


async def addmaintainer(update, context):
    if update.effective_chat.id != Constants.root:
        await update.effective_chat.send_message('Only the root admin can manage maintainers.')
        return

    user_id, name = _resolve_user(update, context)
    if user_id is None:
        await update.effective_chat.send_message(_MAINTAINER_USAGE, parse_mode='Markdown')
        return

    if user_id in Options.allowed_ids:
        await update.effective_chat.send_message(f'{name} already has access.')
        return

    Options.add_id(user_id, name)
    logger.info('Added user %s (%s)', name, user_id)
    await update.effective_chat.send_message(f'Added {name} ({user_id}).')


async def removemaintainer(update, context):
    if update.effective_chat.id != Constants.root:
        await update.effective_chat.send_message('Only the root admin can remove users.')
        return

    others = [uid for uid in Options.allowed_ids if uid != Constants.root]
    if not others:
        await update.effective_chat.send_message('No users to remove.')
        return

    keyboard = []
    for uid in others:
        label = Options.user_names.get(str(uid), str(uid))
        keyboard.append([InlineKeyboardButton(label, callback_data=f'remove:{uid}')])

    await update.effective_chat.send_message(
        'Select a user to remove:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def remove_callback(update, context):
    query = update.callback_query
    await query.answer()

    if update.effective_chat.id != Constants.root:
        await query.edit_message_text('Access denied.')
        return

    uid = int(query.data.split(':')[1])
    name = Options.user_names.get(str(uid), str(uid))

    if uid not in Options.allowed_ids:
        await query.edit_message_text(f'{name} is not in the user list.')
        return

    Options.remove_id(uid)
    logger.info('Removed user %s (%s)', name, uid)
    await query.edit_message_text(f'Removed {name}.')


async def listmaintainers(update, context):
    if update.effective_chat.id != Constants.root:
        await update.effective_chat.send_message('Only the root admin can view the user list.')
        return

    others = [uid for uid in Options.allowed_ids if uid != Constants.root]
    if not others:
        await update.effective_chat.send_message('No users added yet.')
        return

    lines = "\n".join(f"• {uid}" for uid in others)
    await update.effective_chat.send_message(f'Allowed users:\n{lines}')


def make_application():
    token = os.environ['BOT_TOKEN']
    logger.info(f'Token: {token}')

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("brightness", brightness))
    app.add_handler(CommandHandler("text_speed", text_speed))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("program", program))
    app.add_handler(CommandHandler("programs", programs))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("addmaintainer", addmaintainer))
    app.add_handler(CommandHandler("removemaintainer", removemaintainer))
    app.add_handler(CommandHandler("listmaintainers", listmaintainers))
    app.add_handler(CallbackQueryHandler(remove_callback, pattern=r'^remove:'))

    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))
    app.add_handler(MessageHandler(filters.CONTACT, access_handler))
    app.add_handler(MessageHandler(filters.Document.MimeType("video/mp4"), gif_handler))
    app.add_handler(MessageHandler(filters.TEXT, text))

    # Group 1: runs for every message regardless of what group 0 did
    app.add_handler(MessageHandler(filters.ALL, relay_to_root), group=1)

    app.add_error_handler(error)

    return app


stopped = False


class System:
    def __init__(self):
        logger.info('##########################   bot  #########')
        logger.info("Setting up queues")
        q.setup()
        txt.setup()
        self.app = make_application()

    async def _run(self, pill: threading.Event) -> None:
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Bot polling started")
        while not pill.is_set():
            await asyncio.sleep(0.5)
        logger.info("Bot stopping…")
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    def start(self, pill: threading.Event = threading.Event()) -> None:
        import asyncio as _asyncio
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run(pill))
        finally:
            loop.close()

    def stop(self):
        global stopped
        if not stopped:
            stopped = True
            self.app.stop_running()
        else:
            logger.info("Stop already initiated")


def main(pill: threading.Event = threading.Event()) -> None:
    s = System()
    s.start(pill)


if __name__ == '__main__':
    s = System()

    def handler(signal_received, frame):
        logger.info('SIGINT or CTRL-C detected. Exiting gracefully')
        s.stop()
        sys.exit(0)

    signal(SIGINT, handler)

    print('Running. Press CTRL-C to exit.')
    s.start()
