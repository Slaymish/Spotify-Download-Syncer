#!/usr/bin/env python3
"""
Diagnostic tool for soulseek-cli issues
"""
import subprocess
import os
import shutil
import time

def test_soulseek_directly():
    """Test soulseek-cli directly to diagnose issues"""
    print("🔍 Soulseek CLI Diagnostic Tool")
    print("=" * 50)
    
    # Check if soulseek is in PATH
    soulseek_path = shutil.which("soulseek")
    print(f"📍 Soulseek path: {soulseek_path}")
    
    if not soulseek_path:
        print("❌ soulseek-cli not found in PATH")
        return
    
    # Test basic command
    print("\n🧪 Testing basic soulseek command...")
    try:
        result = subprocess.run(["soulseek", "--help"], 
                              capture_output=True, text=True, timeout=10)
        print(f"✅ Help command exit code: {result.returncode}")
        if result.stdout:
            print(f"📄 Help output (first 200 chars): {result.stdout[:200]}...")
    except subprocess.TimeoutExpired:
        print("⏰ Help command timed out")
    except Exception as e:
        print(f"❌ Help command failed: {e}")
    
    # Test query command with short timeout
    print("\n🧪 Testing query command...")
    cmd = ["soulseek", "query", "test"]
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=15)
            elapsed = time.time() - start_time
            print(f"✅ Query completed in {elapsed:.1f}s")
            print(f"📤 Exit code: {process.returncode}")
            
            if stdout:
                print(f"📄 Stdout ({len(stdout)} chars): {stdout[:300]}...")
            if stderr:
                print(f"📄 Stderr ({len(stderr)} chars): {stderr[:300]}...")
                
        except subprocess.TimeoutExpired:
            process.kill()
            elapsed = time.time() - start_time
            print(f"⏰ Query timed out after {elapsed:.1f}s")
            print("💡 This suggests the query command is hanging")
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")
    
    print("\n🏁 Diagnostic complete!")
    print("\n💡 If queries are timing out:")
    print("   1. Check your internet connection")
    print("   2. Try running 'soulseek q test' manually in terminal")
    print("   3. Check if soulseek-cli needs configuration")

if __name__ == "__main__":
    test_soulseek_directly()
