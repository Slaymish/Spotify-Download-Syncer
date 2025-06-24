import os.path


def test_soulseek(song):
	pass



def main():
	songs = [
			'messy by oeahgou',
			'song 2',
			'song 3',
			'song 4'
			]

	test_passed = 0

	for song in songs:
		# will try and download song
		test_soulseek(song)

		# check if exists (like the .mp3)
		exists = os.path.isfile(song)

		# if exists, incremented test_passed by 1
		if exists:
			test_passed += 1
		else:
			print(f"{song} failed to download")


	print("Tests finished")
	print(f"{test_passed}/{len(songs)} passed")



if __name__ == "__main__":
	main()

