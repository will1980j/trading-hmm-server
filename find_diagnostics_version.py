import requests

repo = "will1980j/trading-hmm-server"
file_path = "automated_signals_dashboard.html"

print("🔍 Searching for version with diagnostics iframe...\n")

commits_url = f"https://api.github.com/repos/{repo}/commits?path={file_path}&per_page=50"
response = requests.get(commits_url)

if response.status_code == 200:
    commits = response.json()
    
    for i, commit in enumerate(commits):
        sha = commit['sha']
        date = commit['commit']['author']['date']
        message = commit['commit']['message']
        
        # Fetch file from this commit
        file_url = f"https://raw.githubusercontent.com/{repo}/{sha}/{file_path}"
        file_response = requests.get(file_url)
        
        if file_response.status_code == 200:
            content = file_response.text
            has_iframe = '<iframe' in content
            has_diagnostic = 'diagnostic' in content.lower()
            has_live_diagnostic = 'live-diagnostics-terminal' in content.lower()
            
            if has_iframe or has_diagnostic or has_live_diagnostic:
                print(f"✅ {sha[:8]} - {date[:10]} - {message[:40]}")
                print(f"   iframe: {has_iframe}, diagnostic: {has_diagnostic}, live-diag: {has_live_diagnostic}")
                
                if has_iframe and (has_diagnostic or has_live_diagnostic):
                    print(f"\n🎯 FOUND IT! Commit {sha[:8]} has diagnostics iframe!")
                    filename = f"DASHBOARD_WITH_DIAGNOSTICS_{sha[:8]}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"📁 Saved as: {filename}")
                    print(f"📊 Size: {len(content)} bytes")
                    break
            else:
                if i < 10:  # Only show first 10
                    print(f"   {sha[:8]} - {date[:10]} - No diagnostics")
else:
    print(f"❌ Failed: {response.status_code}")
