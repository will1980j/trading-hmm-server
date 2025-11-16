# Railway Volume Video Storage Setup

## What This Does
Stores your 86 videos on Railway's persistent volume storage for fast, reliable delivery worldwide.

## Cost
- **$0.25/GB/month**
- 86 videos at 10-50MB each = ~2-4GB = **$0.50-$1.00/month**
- If you compress videos to 2-3MB each = ~250MB = **$0.06/month**

## Setup Steps

### 1. Create Volume in Railway Dashboard
1. Go to https://railway.app/dashboard
2. Select your project
3. Click your service
4. Go to "Variables" tab
5. Scroll to "Volumes" section
6. Click "+ New Volume"
7. Set:
   - Mount Path: `/app/videos`
   - Size: 5GB (or 1GB if using compressed videos)
8. Click "Add"
9. **Redeploy your service** (Railway will mount the volume)

### 2. Upload Videos to Volume

**Option A: Upload via Script (Recommended)**
Run the `upload_videos_to_volume.py` script I created. It will:
- Download all 86 videos from Google Drive
- Upload them to Railway volume
- One-time operation

**Option B: Manual Upload**
Use Railway CLI to upload videos directly:
```bash
railway volume mount /app/videos
# Then copy videos to the mounted directory
```

### 3. Update HTML Files
Change video sources from:
```javascript
'/proxy-video/FILE_ID'
```
To:
```javascript
'/volume-video/video1.mp4'
```

### 4. Add Video Serving Endpoint
Add to `web_server.py`:
```python
@app.route('/volume-video/<filename>')
def serve_volume_video(filename):
    video_path = f'/app/videos/{filename}'
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    return "Video not found", 404
```

## Benefits
- ✅ Videos survive redeployments
- ✅ Fast delivery (same datacenter as app)
- ✅ One-time upload
- ✅ No external dependencies
- ✅ Works globally

## Drawbacks
- ❌ Costs $0.25/GB/month (~$0.50-$1/month for your videos)
- ❌ Not a global CDN (single region)
- ❌ Requires initial upload process

## Next Steps
1. Create volume in Railway dashboard
2. Redeploy service
3. Run upload script
4. Update HTML files
5. Deploy changes
