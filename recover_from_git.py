import os
import subprocess

# Try to recover the file from git history
commits_to_try = [
    "63eb6ca73e9aca65ab2273f3cbe2bf506d848b52",  # Most recent
    "5c38f822a95286a8beb982756466ab557e745d80",
    "309257e7f612f99088a597f54046cf17befcb590",
    "80f6b4edc7b13ac2b613d3918d252b0b16c83392",
    "d587b3f76d275ae36db441383efa11a5a78da3b2",
    "ee31d31508b0c79d45992035beb3b1f56c2e15d1",
    "e884fe8640c323591e742ac49c1ebc787655d9b3",
]

# Check if git is available via full path
git_paths = [
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\bin\git.exe",
    r"C:\Users\wnj\AppData\Local\Programs\Git\bin\git.exe",
]

git_cmd = None
for path in git_paths:
    if os.path.exists(path):
        git_cmd = path
        print(f"✅ Found git at: {path}")
        break

if not git_cmd:
    print("❌ Git not found. Trying 'git' command anyway...")
    git_cmd = "git"

# Try each commit
for commit in commits_to_try:
    try:
        print(f"\n🔍 Trying commit: {commit[:8]}...")
        result = subprocess.run(
            [git_cmd, "show", f"{commit}:automated_signals_dashboard.html"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and len(result.stdout) > 1000:
            filename = f"RECOVERED_FROM_{commit[:8]}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"✅ SUCCESS! Recovered file from commit {commit[:8]}")
            print(f"📁 Saved as: {filename}")
            print(f"📊 File size: {len(result.stdout)} bytes")
            
            # Check for diagnostics
            if '<iframe' in result.stdout and 'diagnostic' in result.stdout.lower():
                print("✅ DIAGNOSTICS IFRAME FOUND!")
            else:
                print("ℹ️  No diagnostics iframe in this version")
            break
        else:
            print(f"   File not in this commit or error occurred")
            
    except Exception as e:
        print(f"   Error: {e}")
        continue
else:
    print("\n❌ Could not recover file from any commit")
    print("Git may not be installed or accessible")
