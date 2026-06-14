import logging
import multiprocessing
import signal
import sys
import threading

import blinky
import blinky_bot
import blinky_interface

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger('flaschplayer')


class BlinkyStarter:

    def __init__(self):
        self.pill2kill = threading.Event()
        self.blinky_thread = threading.Thread(
            target=blinky.main,
            kwargs={'pill': self.pill2kill},
            name='blinky',
            daemon=True,
        )
        self.bot_thread = threading.Thread(
            target=blinky_bot.main,
            kwargs={'pill': self.pill2kill},
            name='blinky_bot',
            daemon=True,
        )
        self.interface_process = multiprocessing.Process(
            target=blinky_interface.main,
            name='blinky_interface',
        )

    def start(self):
        logger.info('Starting blinky (display loop)')
        self.blinky_thread.start()
        logger.info('Starting blinky_bot (Telegram)')
        self.bot_thread.start()
        logger.info('Starting blinky_interface (web UI)')
        self.interface_process.start()

    def stop(self):
        logger.info('Stopping…')
        self.pill2kill.set()
        if self.interface_process.is_alive():
            self.interface_process.terminate()
            self.interface_process.join(timeout=5)
        self.blinky_thread.join(timeout=5)
        # bot thread is daemon — exits with the process

    def run(self):
        self.start()
        try:
            while True:
                self.pill2kill.wait(1)
                if not self.blinky_thread.is_alive():
                    logger.warning('blinky thread exited unexpectedly')
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


if __name__ == '__main__':
    starter = BlinkyStarter()

    def _handle_signal(signum, frame):
        logger.info('Received signal %s, shutting down', signum)
        starter.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    starter.run()
