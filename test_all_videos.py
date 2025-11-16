"""
Test All 91 Videos and Generate Clean List
Tests each video URL and creates a list of only working videos
"""

import requests
import time

# All 91 video IDs from your homepage
VIDEO_IDS = [
    '18gYaw4YLy0r4-N-NVFP7MTRyRBbhCH1i',
    '1CG1XiGaTutLOi6atmm3vBb-jOferAy3R',
    '107-c9jR3b4y0whP3OLyq6eTKRPMFhKY9',
    '1zh1Enf8cESXVzeBtM6G_9Ho-Is-0AFa1',
    '1I0odad2sA3IWsFXvYxqln6pOhUsmWemX',
    '1jB3QkgI8hRtFZmCou21oSPvrHmfzptmZ',
    '15mOVz4TzU1Nh2u9C0De0iN5B8NGRQcxE',
    '1Q-Jtepx2aLMesunbbepoJUSiIHEBr3Hv',
    '1C0h1z9uPjnoEGOkzhPskZEHLPn4OGrfd',
    '1ad9n0y97uYskUN2KaFxxz4EzUlmMxi1x',
    '1khedd5UyYnDKrlaXdpJjA7VuRv1nskJJ',
    '1AW4j_MY9MI8EzouChHUQP-fY30pEeba7',
    '1XaGv5BG_Z9VytOPEVeE0SZrGJpvRgYbh',
    '1kwjMpTkvGo25sdrAjPun7JPNnZ58FBGa',
    '1IDxcL7yJeNG9iwclMcckMGxAVTofLrGH',
    '1RBOsdJOuFAXtomQ-9Q_kR2h8uQatjAnH',
    '1jU83_jjYOZWLmLicAGIrQEbAejqWGdpV',
    '1VqcyCE-PW-DL74nd39KPw2Go79ioIjCE',
    '1fMCRFCWVv_LL5IiHPbd5aojlZ05MXboW',
    '1EDG_7sNCCSQBzg64FP1rRSgYdQSU2BW5',
    '12ulHcA5IG305qLU2kMEklr03RcmoGGMX',
    '1OwvgPkDU62fcAmOx62wo0mnzY4EhgA-4',
    '1mJzqn5UYQxlf2Zk_niMvqmOIthK-On-0',
    '1zqPreHTtNrQ3iN-kEc19JxQjinFuLXbL',
    '1NJORsHhEu_TAUEflGsDjO5laKjX9QuLg',
    '1EqwMQgs-vFpBz4-uBOzrEIZ3YDZFbF0E',
    '1kwuZHhlB3fiwfNw1EWAS0hDbw20SSfVs',
    '1HtWhyT2ZA8-adr2yfXVeMsFPvj9rZ5IO',
    '1G0x-fBKdRxKseFlboVtRHRVZJIyKQ4gy',
    '1nk3OsC0x0IQ-CeqZqs4zFEieRZepoTaL',
    '1US_QE8bAwTphvHeTqgZhqrhrw3OvtRxe',
    '14GLMh3SMZ0sRo4L40tgHNR38qBns0Gda',
    '1Y9MZ8_IWKwKTxSWg6ZH0y-euN55RC-Tf',
    '1L1uFB1o1AraIP0UrMdgA_jO05pW9xj-p',
    '1sEpLjDhfffJQJfsH9HIKbKapICmT65OL',
    '1YAt-MgYSfxCXpR5_Tm72ZP84ki0tPihD',
    '1xmPAU3TqBuzypfL8B3jhy3RehvMnZadH',
    '1BigKqxPcEQM7PrSo3v1oq2fqLkVElsH1',
    '1ob580n1fv7F7kXQThTiXnzmp87h6KFsg',
    '1Dj7K90riE6sCgCdLMhfV4PWBwb0vZTO_',
    '1uklkLn8qQXJkJBLWzlQb58VB4MVqkcYd',
    '1oUKWC-ln3hmupPXvZr38mf6cv_gfom1O',
    '1wjrO9MAAkzUxHpUYU9772nDLnELO_VxD',
    '1HkMKp2ThPaTH56su2a-R5UNml9OWtSCG',
    '1j7QOuy8YJHWKp3SfqQJ9ZX0cp7YVTwjD',
    '1NuThygDJNqsh9sp0TiDMLsUb9r6DlYJ4',
    '1n49QdArYSCXhec3WjcswlDR5vvEZweAR',
    '1peCksjeTKtodRXy6t_NwzqnRTXgIbpQJ',
    '1rCfPR9gJM6dF9WGf0peJV9xaizwla1ND',
    '111_tOFQLQTwJd05jqfll3lAqHGh98gxH',
    '1tXkujWZYhkC9HoZXNfNbj17F37IgnSJ8',
    '1FxLFPHPqM1ijR5lagVZ1dHeOpfjtSynk',
    '1JASFoGmQX2FNLMgzWnEpeTitt8qAh6ih',
    '1PkBcTJMIniyaic4FggwkpBoAbNujSNTJ',
    '19egODctzRMmb_WiiS8WOxdE7N-LRHbYK',
    '16g7F469QGkcjCN7Yd65xPTd-zS9qFPoA',
    '1MI7UxRbU7smv7NXI3SVWsLDw1ilZ7QZF',
    '1tyVPLAsMu9MOtNFn4zGEkwE7kvnzlvVB',
    '1jabECNUhqO6K6ILqj3WJOR0CvVnwKmKa',
    '1Ozo-e9-W_KgsE_D6IDvSThsHAUt5YBT',
    '1TqMT5toWPiMgzaA2QGi_U2w1WZmEbVla',
    '11vQjWV1vl1jCn1rvvkWZmvt7GQpQP_rD',
    '1Fq4mi-okbQ379WajWu3lpqlWT5LCAblW',
    '1BW9VEq_myf2ppAmYngWG45MuZmPvvjzE',
    '1rCATcoBLVYvDOl7ZXhOBOoK3s5jDyMeA',
    '1yfBxNKD2zBgnh4OrIhtt8NtEXQOK1A2R',
    '1qO7_vaqhJ8-LNTHcKUUuLoF8-82UJP5l',
    '159du18lMk4lA6ZDBfGG1uSEtpHcysp2K',
    '1KI3JRNnf9-tqKJ-yE4LDiOV3V5Ibksuj',
    '1nVxcv-bWORlMeCk2_AzHOQXxBa39-Zyt',
    '10ajtednyG0nf37aywJa9omF0sEZ4a9No',
    '1tyAtWhjafHXhoVxjUKR8Q1lFNfNen05M',
    '1MuxkXcFOgqm72UE1n1rCXqG5QrDCpE1m',
    '1OfyB6jxFdYqIGv6D5a5AnVX0pgcUJjNI',
    '1xCG_0-d5ZKr8KCWsAJpvk1Yowh7WDfPI',
    '1TCBk1S3hfbKmof04FsB__gBcznSydnij',
    '1OohFHyNiP9r6GE8w77GNPKfwz3zT4DDc',
    '1IO9YkN4O0YvRngTXccIoU3awaerRkjcr',
    '1jwpuubfpPBvwfP7qJVHvYY5fPiN9WsYn',
    '1lmLAfjcity_xT7AxlGFlHHRV06D04z3b',
    '1uUmdfFPARosedUlpsTG2C9h1eTIWGWJI',
    '1CNLQae2HKcxLj3Wul1n0N_Oh-9WecHHW',
    '1Exb8-ruty_wah8J_09zCfHmd2qlQNuhU',
    '1pONgmrTnvAJSEc0JAY1pMyw5pZCAN_DS',
    '12cNNkIN1ybmpmeau5ojNtURR52fPRq93',
    '1VbLpwu8vqsFAjTlf3DeLNe6DwUA0Bcxz',
    '1ADaw_LPHI-pukTnbIYxaEVytMNt-2woV',
    '1vireVrDSCsdtZJKLYTLgmTsO8ZzbkTfy',
    '1Foxzw6Ize-OKaAs_Rvh0kK17YcTsyxXk',
    '1LQyC24BsWyBs84kdCu1TViaih7irBsEd',
    '12GbOhExy_O4tm8U6730Ca5yr0OKQud-'
]

BASE_URL = 'https://web-production-cd33.up.railway.app/proxy-video/'

def test_video(video_id, index):
    """Test if a video URL returns 200 OK"""
    url = f"{BASE_URL}{video_id}"
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            print(f"✅ Video {index + 1}/91: {video_id} - WORKING")
            return True
        else:
            print(f"❌ Video {index + 1}/91: {video_id} - FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Video {index + 1}/91: {video_id} - ERROR ({str(e)})")
        return False

def main():
    print("=" * 70)
    print("Testing All 91 Videos")
    print("=" * 70)
    print()
    
    working_videos = []
    broken_videos = []
    
    for i, video_id in enumerate(VIDEO_IDS):
        if test_video(video_id, i):
            working_videos.append(video_id)
        else:
            broken_videos.append(video_id)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✅ Working videos: {len(working_videos)}/91")
    print(f"❌ Broken videos: {len(broken_videos)}/91")
    print()
    
    # Save working videos to file
    with open('working_videos.txt', 'w') as f:
        f.write("// Working Video IDs (Ready to use)\n")
        f.write("const videoSources = [\n")
        for video_id in working_videos:
            f.write(f"    '/proxy-video/{video_id}',\n")
        f.write("];\n")
    
    print("✅ Working videos saved to: working_videos.txt")
    print()
    
    # Save broken videos for reference
    if broken_videos:
        with open('broken_videos.txt', 'w') as f:
            f.write("// Broken Video IDs (404 errors)\n")
            for video_id in broken_videos:
                f.write(f"{video_id}\n")
        print("❌ Broken videos saved to: broken_videos.txt")
    
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the videoSources array from working_videos.txt")
    print("2. Replace the videoSources array in homepage_video_background.html")
    print("3. Replace the videoSources array in login_video_background.html")
    print("4. Commit and deploy to Railway")
    print("=" * 70)

if __name__ == '__main__':
    main()
