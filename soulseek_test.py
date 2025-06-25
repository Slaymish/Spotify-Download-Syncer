import os.path
from spotify_syncer.torrent_searchers import SoulseekSearcher
import shutil
from spotify_syncer.config import DOWNLOAD_DIR
import signal
import time
import logging

# Set up logging to see detailed progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Search timed out")

def test_soulseek(song, searcher, timeout_seconds=120):
    """Test soulseek search with timeout to prevent hanging"""
    print(f"  Starting search for: {song} (timeout: {timeout_seconds}s)")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        start_time = time.time()
        file = searcher.search(song)
        elapsed = time.time() - start_time
        signal.alarm(0)  # Cancel the alarm
        print(f"  Search completed in {elapsed:.1f}s")
        return file
    except TimeoutError:
        print(f"  ⚠️  Search timed out after {timeout_seconds} seconds")
        return None
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        print(f"  ❌ Search failed with error: {e}")
        return None



def main():
    print("🎯 Starting Soulseek tests....")
    
    # Check download directory
    print(f"📁 Download directory: {DOWNLOAD_DIR}")
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"⚠️  Download directory doesn't exist, creating: {DOWNLOAD_DIR}")
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # make sure soulseekcli exists
    soulseek_path = shutil.which('soulseek')
    if not soulseek_path:
        print("❌ soulseek-cli not found, please install it with:")
        print("   npm install -g soulseek-cli")
        return
    else:
        print(f"✅ Found soulseek-cli at: {soulseek_path}")

    songs = [
        'The Beatles - Hey Jude',
        'Queen - Bohemian Rhapsody', 
        'Led Zeppelin - Stairway to Heaven',
        'Pink Floyd - Wish You Were Here'
    ]

    test_passed = 0
    searcher = SoulseekSearcher()
    print("✅ Created searcher object")

    for song in songs:
        print(f"\n🎵 Processing: {song}")

        # will try and download song with timeout
        file = test_soulseek(song, searcher, timeout_seconds=10)

        if file:
            print(f"  ✅ Search returned: {file}")
        else:
            print(f"  ❌ Search returned None")

        # check if exists (like the .mp3)
        if file and file.startswith('file://'):
            file_path = file[7:]
            exists = os.path.exists(file_path)
            if exists:
                file_size = os.path.getsize(file_path)
                print(f"  ✅ File found: {file_path} ({file_size} bytes)")
            else:
                print(f"  ❌ File path doesn't exist: {file_path}")
        else:
            exists = False
            print(f"  ❌ No valid file path returned")

        # if exists, incremented test_passed by 1
        if exists:
            test_passed += 1
        else:
            print(f"  ❌ {song} failed to download")


    print(f"\n🏁 Tests finished!")
    print(f"📊 Results: {test_passed}/{len(songs)} passed")
    
    if test_passed == 0:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure soulseek-cli is properly configured")
        print("   2. Check if you have Soulseek network access")
        print("   3. Try simpler, more popular song names")
        print("   4. Check the logs for specific error messages")
    elif test_passed < len(songs):
        print(f"\n✅ Partial success! {test_passed} downloads completed.")
    else:
        print(f"\n🎉 All tests passed! All {test_passed} songs downloaded successfully.")



if __name__ == "__main__":
	main()

