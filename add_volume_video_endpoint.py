"""
Add Volume Video Serving Endpoint to web_server.py
"""

VOLUME_VIDEO_ENDPOINT = '''
# ============================================================================
# RAILWAY VOLUME VIDEO SERVING
# ============================================================================

@app.route('/volume-video/<filename>')
def serve_volume_video(filename):
    """Serve videos from Railway persistent volume"""
    import os
    from flask import send_file, abort
    
    # Security: only allow .mp4 files
    if not filename.endswith('.mp4'):
        abort(404)
    
    # Volume mount path
    volume_path = '/app/videos'
    video_path = os.path.join(volume_path, filename)
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        abort(404)
    
    # Serve with caching headers for performance
    response = send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=False,
        download_name=filename
    )
    
    # Cache for 24 hours
    response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['Accept-Ranges'] = 'bytes'
    
    return response

@app.route('/volume-video-list')
def list_volume_videos():
    """List all videos in volume (for debugging)"""
    import os
    import json
    
    volume_path = '/app/videos'
    
    if not os.path.exists(volume_path):
        return json.dumps({"error": "Volume not mounted"}), 404
    
    videos = [f for f in os.listdir(volume_path) if f.endswith('.mp4')]
    videos.sort()
    
    return json.dumps({
        "count": len(videos),
        "videos": videos,
        "total_size_mb": sum(
            os.path.getsize(os.path.join(volume_path, f)) 
            for f in videos
        ) / (1024 * 1024)
    })
'''

print("=" * 60)
print("Add Volume Video Endpoint to web_server.py")
print("=" * 60)
print()
print("Add this code to your web_server.py file:")
print()
print(VOLUME_VIDEO_ENDPOINT)
print()
print("=" * 60)
print("Then update your HTML files to use:")
print("  '/volume-video/video001.mp4'")
print("  '/volume-video/video002.mp4'")
print("  etc.")
print("=" * 60)
