import os
import zlib
import hashlib

def read_git_object(sha):
    """Read a git object directly from .git/objects"""
    obj_dir = sha[:2]
    obj_file = sha[2:]
    path = f".git/objects/{obj_dir}/{obj_file}"
    
    if not os.path.exists(path):
        return None
    
    try:
        with open(path, 'rb') as f:
            compressed = f.read()
            decompressed = zlib.decompress(compressed)
            return decompressed
    except Exception as e:
        print(f"Error reading {sha}: {e}")
        return None

# Commits to check
commits = [
    "63eb6ca73e9aca65ab2273f3cbe2bf506d848b52",
    "5c38f822a95286a8beb982756466ab557e745d80",
    "309257e7f612f99088a597f54046cf17befcb590",
]

print("🔍 Searching git objects for automated_signals_dashboard.html...\n")

for commit_sha in commits:
    print(f"Checking commit: {commit_sha[:8]}...")
    obj = read_git_object(commit_sha)
    
    if obj:
        # Parse commit object to find tree
        obj_str = obj.decode('utf-8', errors='ignore')
        if 'tree ' in obj_str:
            tree_line = [line for line in obj_str.split('\n') if line.startswith('tree')]
            if tree_line:
                tree_sha = tree_line[0].split()[1]
                print(f"  Found tree: {tree_sha[:8]}")
                
                # Read tree object
                tree_obj = read_git_object(tree_sha)
                if tree_obj and b'automated_signals_dashboard.html' in tree_obj:
                    print(f"  ✅ File found in this commit!")
                    # Extract blob SHA for the file
                    # This is complex - would need full git parser
                    print(f"  Commit {commit_sha[:8]} contains the file")
                else:
                    print(f"  File not in root tree")
    else:
        print(f"  Could not read commit object")
    print()

print("\n💡 Since git command line isn't available, please:")
print("1. Go to your GitHub repository in a web browser")
print("2. Navigate to the file: automated_signals_dashboard.html")
print("3. Click 'History' button")
print("4. Find a commit from before today")
print("5. Click 'View file' and copy the content")
