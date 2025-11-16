"""
Upload Videos to Railway Volume
One-time script to download videos from Google Drive and upload to Railway volume
"""

import os
import requests
from pathlib import Path

# Your 86 video IDs
VIDEO_IDS = [
    '18gYaw4YLy0r4-N-NVFP7MTRyRBbhCH1i',
    '1CG1XiGaTutLOi6atmm3vBb-jOferAy3R',
    '107-c9jR3b4y0whP3OLyq6eTKRPMFhKY9',
    # ... (all 86 IDs)
]

VOLUME_PATH = '/app/videos'  # Railway volume mount path
GOOGLE_DRIVE_URL = 'https://drive.google.com/uc?export=download&id='

def download_and_save_video(video_id, index):
    """Download video from Google Drive and save to volume"""
    try:
        print(f"Downloading video {index + 1}/86 (ID: {video_id})...")
        
        # Download from Google Drive
        url = f"{GOOGLE_DRIVE_URL}{video_id}"
        response = requests.get(url, stream=True, timeout=300)
        
        if response.status_code == 200:
            # Save to volume
            filename = f"video{index + 1:03d}.mp4"  # video001.mp4, video002.mp4, etc.
            filepath = os.path.join(VOLUME_PATH, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"✅ Saved {filename} ({file_size:.2f} MB)")
            return True
        else:
            print(f"❌ Failed to download video {index + 1}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading video {index + 1}: {e}")
        return False

def main():
    """Main upload process"""
    print("=" * 60)
    print("Railway Volume Video Upload")
    print("=" * 60)
    print()
    
    # Check if volume is mounted
    if not os.path.exists(VOLUME_PATH):
        print(f"❌ Volume not mounted at {VOLUME_PATH}")
        print("Please create volume in Railway dashboard and redeploy first!")
        return
    
    print(f"✅ Volume found at {VOLUME_PATH}")
    print(f"📦 Uploading {len(VIDEO_IDS)} videos...")
    print()
    
    # Create volume directory if needed
    os.makedirs(VOLUME_PATH, exist_ok=True)
    
    # Download and save all videos
    success_count = 0
    for i, video_id in enumerate(VIDEO_IDS):
        if download_and_save_video(video_id, i):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Upload Complete: {success_count}/{len(VIDEO_IDS)} videos uploaded")
    print("=" * 60)
    
    # Calculate total size
    total_size = sum(
        os.path.getsize(os.path.join(VOLUME_PATH, f)) 
        for f in os.listdir(VOLUME_PATH) 
        if f.endswith('.mp4')
    ) / (1024 * 1024 * 1024)  # GB
    
    print(f"Total storage used: {total_size:.2f} GB")
    print(f"Estimated monthly cost: ${total_size * 0.25:.2f}")

if __name__ == '__main__':
    main()
