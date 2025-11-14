import requests

# GitHub API to get commit history
repo = "will1980j/trading-hmm-server"
file_path = "automated_signals_dashboard.html"

print("🔍 Fetching commit history from GitHub...\n")

# Get commits for this file
commits_url = f"https://api.github.com/repos/{repo}/commits?path={file_path}"
response = requests.get(commits_url)

if response.status_code == 200:
    commits = response.json()
    print(f"✅ Found {len(commits)} commits for this file\n")
    
    # Try the most recent commits (skip the very latest which might be the deletion)
    for i, commit in enumerate(commits[:10]):
        sha = commit['sha']
        date = commit['commit']['author']['date']
        message = commit['commit']['message']
        
        print(f"{i+1}. {sha[:8]} - {date[:10]} - {message[:50]}")
        
        # Try to fetch the file from this commit
        file_url = f"https://raw.githubusercontent.com/{repo}/{sha}/{file_path}"
        file_response = requests.get(file_url)
        
        if file_response.status_code == 200 and len(file_response.text) > 1000:
            filename = f"RECOVERED_FROM_GITHUB_{sha[:8]}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(file_response.text)
            
            print(f"\n✅ SUCCESS! Recovered file from commit {sha[:8]}")
            print(f"📁 Saved as: {filename}")
            print(f"📊 File size: {len(file_response.text)} bytes")
            print(f"📅 Commit date: {date}")
            print(f"💬 Commit message: {message}")
            
            # Check for diagnostics
            if '<iframe' in file_response.text and 'diagnostic' in file_response.text.lower():
                print("✅ DIAGNOSTICS IFRAME FOUND!")
            else:
                print("ℹ️  No diagnostics iframe in this version")
            
            # Save as the main file
            with open("automated_signals_dashboard.html", "w", encoding="utf-8") as f:
                f.write(file_response.text)
            print(f"\n✅ Restored to: automated_signals_dashboard.html")
            break
    else:
        print("\n❌ Could not recover file from any commit")
else:
    print(f"❌ Failed to fetch commits: {response.status_code}")
    print(f"Response: {response.text[:200]}")
