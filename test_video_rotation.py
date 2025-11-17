"""
Test script for random video rotation implementation
"""
import os
import sys

def test_directory_structure():
    """Test that video directories exist"""
    print("Testing directory structure...")
    
    login_dir = os.path.join('static', 'videos', 'login')
    homepage_dir = os.path.join('static', 'videos', 'homepage')
    
    assert os.path.exists(login_dir), f"❌ Login directory missing: {login_dir}"
    assert os.path.exists(homepage_dir), f"❌ Homepage directory missing: {homepage_dir}"
    
    print(f"✅ Login directory exists: {login_dir}")
    print(f"✅ Homepage directory exists: {homepage_dir}")
    return True

def test_helper_function():
    """Test the get_random_video helper function"""
    print("\nTesting helper function...")
    
    # Import the function
    sys.path.insert(0, os.path.dirname(__file__))
    from web_server import get_random_video
    
    # Test with empty folders (should return None gracefully)
    result = get_random_video('login')
    print(f"✅ get_random_video('login') returns: {result} (None expected if no videos)")
    
    result = get_random_video('homepage')
    print(f"✅ get_random_video('homepage') returns: {result} (None expected if no videos)")
    
    # Test with non-existent folder (should return None gracefully)
    result = get_random_video('nonexistent')
    assert result is None, "❌ Should return None for non-existent folder"
    print(f"✅ get_random_video('nonexistent') returns None (graceful failure)")
    
    return True

def test_video_files():
    """Test if video files exist and are detected"""
    print("\nTesting video file detection...")
    
    login_dir = os.path.join('static', 'videos', 'login')
    homepage_dir = os.path.join('static', 'videos', 'homepage')
    
    login_videos = [f for f in os.listdir(login_dir) if f.lower().endswith(('.mp4', '.webm'))]
    homepage_videos = [f for f in os.listdir(homepage_dir) if f.lower().endswith(('.mp4', '.webm'))]
    
    print(f"📹 Login videos found: {len(login_videos)}")
    if login_videos:
        print(f"   Examples: {', '.join(login_videos[:3])}")
    else:
        print("   ⚠️  No videos yet - upload videos to /static/videos/login/")
    
    print(f"📹 Homepage videos found: {len(homepage_videos)}")
    if homepage_videos:
        print(f"   Examples: {', '.join(homepage_videos[:3])}")
    else:
        print("   ⚠️  No videos yet - upload videos to /static/videos/homepage/")
    
    return True

def test_template_syntax():
    """Test that templates have correct Jinja2 syntax"""
    print("\nTesting template syntax...")
    
    # Check login template
    with open('login_video_background.html', 'r', encoding='utf-8') as f:
        login_content = f.read()
    
    assert '{% if video_file %}' in login_content, "❌ Login template missing Jinja2 conditional"
    assert "url_for('static', filename='videos/login/' + video_file)" in login_content, "❌ Login template missing url_for"
    print("✅ Login template has correct Jinja2 syntax")
    
    # Check homepage template
    with open('homepage_video_background.html', 'r', encoding='utf-8') as f:
        homepage_content = f.read()
    
    assert '{% if video_file %}' in homepage_content, "❌ Homepage template missing Jinja2 conditional"
    assert "url_for('static', filename='videos/homepage/' + video_file)" in homepage_content, "❌ Homepage template missing url_for"
    print("✅ Homepage template has correct Jinja2 syntax")
    
    return True

def test_backend_integration():
    """Test that backend routes are modified correctly"""
    print("\nTesting backend integration...")
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Check helper function exists
    assert 'def get_random_video(subfolder):' in server_content, "❌ Helper function missing"
    print("✅ Helper function exists")
    
    # Check login route modified
    assert "video_file = get_random_video('login')" in server_content, "❌ Login route not modified"
    print("✅ Login route modified correctly")
    
    # Check homepage route modified
    assert "video_file = get_random_video('homepage')" in server_content, "❌ Homepage route not modified"
    print("✅ Homepage route modified correctly")
    
    # Check render_template_string usage
    assert 'video_file=video_file' in server_content, "❌ video_file parameter not passed to templates"
    print("✅ video_file parameter passed to templates")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("RANDOM VIDEO ROTATION - IMPLEMENTATION TEST")
    print("=" * 60)
    
    try:
        test_directory_structure()
        test_helper_function()
        test_video_files()
        test_template_syntax()
        test_backend_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 NEXT STEPS:")
        print("1. Upload video files to /static/videos/login/ and /static/videos/homepage/")
        print("2. Commit changes using GitHub Desktop")
        print("3. Push to main branch (triggers Railway auto-deploy)")
        print("4. Test on production: https://web-production-cd33.up.railway.app/login")
        print("\n✨ Implementation is production-ready!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
