import multiprocessing
import threading
import blinky
import blinky_bot
import blinky_interface


class BlinkyStarter:

	def __init__(self):
		self.pill2kill = threading.Event()
		self.blinky: threading.Thread = threading.Thread(target=blinky.main, kwargs={'pill': self.pill2kill})
		self.blinky_bot: threading.Thread = threading.Thread(target=blinky_bot.main)
		self.blinky_interface = multiprocessing.Process(target=blinky_interface.main)

	def stop(self):
		self.pill2kill.set()
		self.blinky.join()
		self.blinky_bot.join()
		self.blinky_interface.terminate()

	def run(self):
		try:
			self.blinky.start()
			self.blinky_bot.start()
			self.blinky_interface.start()
			while True:
				self.pill2kill.wait(1)
		except KeyboardInterrupt:
			self.stop()


if __name__ == '__main__':
	blinky = BlinkyStarter()
	blinky.run()
