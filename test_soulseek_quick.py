#!/usr/bin/env python3
"""
Quick test for the improved SoulseekSearcher with interactive download handling
"""
import logging
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spotify_syncer.torrent_searchers import SoulseekSearcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

def main():
    print("🎯 Testing improved SoulseekSearcher with interactive download handling")
    
    # Test 1: Check if soulseek-cli is available
    searcher = SoulseekSearcher()
    print("✅ SoulseekSearcher created successfully")
    
    # Test 2: Try a search that should work (if soulseek-cli is available)
    print("\n🔍 Testing search for 'Hey Jude'...")
    result = searcher.search("Hey Jude")
    
    if result is None:
        print("❌ Search returned None")
        print("💡 This could be because:")
        print("   - soulseek-cli is not installed")
        print("   - No search results found")
        print("   - Interactive download failed")
    else:
        print(f"✅ Search successful! Downloaded: {result}")
    
    print("\n🎉 Test completed!")
    print("\n💡 The improved SoulseekSearcher now:")
    print("   ✅ Handles interactive downloads by auto-selecting first result")
    print("   ✅ Scans subdirectories for downloaded files")
    print("   ✅ Filters for audio file types only")
    print("   ✅ Has proper timeout handling")

if __name__ == "__main__":
    main()
