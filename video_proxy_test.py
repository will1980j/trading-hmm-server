"""
Video Proxy Test - Bypass CORS restrictions for Google Drive videos
"""
import requests
from flask import Flask, Response, request
import re

app = Flask(__name__)

def extract_file_id(drive_url):
    """Extract file ID from various Google Drive URL formats"""
    patterns = [
        r'/file/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
        r'/d/([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, drive_url)
        if match:
            return match.group(1)
    return None

def get_direct_download_url(file_id):
    """Convert Google Drive file ID to direct download URL"""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

@app.route('/proxy-video/<file_id>')
def proxy_video(file_id):
    """Proxy Google Drive video through our server to bypass CORS"""
    try:
        # Get the direct download URL
        download_url = get_direct_download_url(file_id)
        
        # Make request to Google Drive
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 200:
            # Create a streaming response
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Set appropriate headers for video streaming
            headers = {
                'Content-Type': response.headers.get('Content-Type', 'video/mp4'),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'public, max-age=3600'
            }
            
            return Response(generate(), headers=headers)
        else:
            return f"Error: Could not fetch video (Status: {response.status_code})", 404
            
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/test-proxy-video')
def test_proxy_video():
    """Test page for video proxy"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Video Proxy</title>
        <style>
            body { margin: 0; padding: 20px; background: #000; color: #fff; font-family: Arial; }
            video { width: 100%; max-width: 800px; height: auto; margin: 20px 0; }
            .status { margin: 10px 0; padding: 10px; background: #333; border-radius: 5px; }
            .test-section { margin: 30px 0; padding: 20px; border: 1px solid #444; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>🎬 Video Proxy Test</h1>
        
        <div class="test-section">
            <h2>Test 1: Your Google Drive Video</h2>
            <div class="status">Testing file ID: 1TCBk1S3hfbKmof04FsB__gBcznSydnij</div>
            <video controls autoplay muted>
                <source src="/proxy-video/1TCBk1S3hfbKmof04FsB__gBcznSydnij" type="video/mp4">
                Your browser does not support video.
            </video>
        </div>
        
        <div class="test-section">
            <h2>Instructions:</h2>
            <p>1. If the video loads and plays, the proxy works! ✅</p>
            <p>2. If it fails, we'll try alternative approaches 🔄</p>
            <p>3. Once working, we can proxy all your nature videos 🌿</p>
        </div>
        
        <script>
            const video = document.querySelector('video');
            const status = document.querySelector('.status');
            
            video.addEventListener('loadstart', () => {
                status.textContent = '🔄 Loading video through proxy...';
                status.style.background = '#1a5490';
            });
            
            video.addEventListener('loadeddata', () => {
                status.textContent = '✅ SUCCESS! Video proxy works!';
                status.style.background = '#0f5132';
            });
            
            video.addEventListener('error', (e) => {
                status.textContent = '❌ Video proxy failed. Error: ' + e.message;
                status.style.background = '#721c24';
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)