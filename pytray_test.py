import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image, ImageDraw, ImageFont
import time

class SpotifyTorrentApp:
	def __init__(self):
		self.icon = pystray.Icon(
			"SpotifyTorrent",
			self._create_image(),
			"SpotifyTorrent",
			menu=Menu(
				Item("Sync Now", self.manual_sync),
				Item("Open Logs", self.open_logs),
				Item("Quit", self.quit_app),
			),
		)

	def _create_image(self):
		# Create a 64x64 icon with the 🎶 emoji
		size = 64
		image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
		draw = ImageDraw.Draw(image)
		font = ImageFont.load_default()
		text = "🎶"
		w = draw.textlength(text,font=font)
		h = font.font.getsize(text)
		draw.text(((size - w) / 2, (size - h) / 2), text, fill="white", font=font)
		return image


	def _auto_sync_loop(self):
		while True:
			time.sleep(300)
			self.manual_sync()

	def manual_sync(self, icon=None, item=None):
		print("syncing!!")

	def _sync(self):
		logging.info("Sync started")
		try:
			self.icon.title = "🔄 syncing..."
			time.sleep(5)
			self.icon.title = "idle"
			logging.info("Sync finished")
		except Exception:
			logging.exception("Exception occurred during sync")


	def open_logs(self, icon=None, item=None):
		opener = "xdg-open"
		subprocess.Popen([opener, LOG_PATH])

	def quit_app(self, icon=None, item=None):
		self.icon.stop()

def main():
	SpotifyTorrentApp().run()


if __name__ == "__main__":
	main()
