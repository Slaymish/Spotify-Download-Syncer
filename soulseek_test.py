import os.path
from spotify_syncer.torrent_searchers import SoulseekSearcher


def test_soulseek(song,searcher):
    # will be None if failed
    file = searcher.search(song)
    return file



def main():
    print("starting test....")
    songs = [
        'messy by oeahgou',
        'song 2',
        'song 3',
        'song 4'
    ]

    test_passed = 0
    searcher = SoulseekSearcher()
    print("created searcher object")

    for song in songs:
        print(f"Processing {song}...")

        # will try and download song
        file = test_soulseek(song,searcher)

        print("Search finished")

        # check if exists (like the .mp3)
        if file:
            exists = os.path.isfile(file)
        else:
            exists = False

        # if exists, incremented test_passed by 1
        if exists:
            test_passed += 1
        else:
            print(f"{song} failed to download")


    print("Tests finished")
    print(f"{test_passed}/{len(songs)} passed")



if __name__ == "__main__":
	main()

