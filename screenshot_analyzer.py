import cv2
import numpy as np
from PIL import Image
import base64
import io
import json
from typing import Dict, List, Tuple, Optional

class ScreenshotAnalyzer:
    def __init__(self):
        pass

    def analyze_screenshot(self, image_data: str) -> Dict:
        """Main analysis function - processes base64 image"""
        try:
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            
            # Phase 2: Pattern Recognition
            fvg_quality = self._analyze_fvg_quality(image)
            confluence_score = self._detect_confluence(image)
            
            # Phase 3: Market Structure
            trend_strength = self._analyze_trend_strength(image)
            setup_quality = self._calculate_setup_quality(fvg_quality, confluence_score, trend_strength)
            
            return {
                'status': 'success',
                'fvg_quality': fvg_quality,
                'confluence_score': confluence_score,
                'trend_strength': trend_strength,
                'setup_quality': setup_quality
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'fvg_quality': 0,
                'confluence_score': 0,
                'trend_strength': 0,
                'setup_quality': 0
            }

    def _decode_base64_image(self, image_data: str) -> np.ndarray:
        """Convert base64 to OpenCV image"""
        # Remove data URL prefix if present
        if 'data:image' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)



    def _analyze_fvg_quality(self, image: np.ndarray) -> float:
        """Phase 2: Analyze FVG quality (0-10 scale)"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges (gaps will have strong vertical edges)
        edges = cv2.Canny(gray, 50, 150)
        
        # Count vertical lines (FVG boundaries)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # Score based on clean vertical boundaries
        vertical_score = np.sum(vertical_lines) / (image.shape[0] * image.shape[1])
        
        # Normalize to 0-10 scale
        return min(10, vertical_score * 1000)

    def _detect_confluence(self, image: np.ndarray) -> float:
        """Detect confluence factors (0-10 scale)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect horizontal lines (support/resistance)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        edges = cv2.Canny(gray, 50, 150)
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Count significant horizontal levels
        line_count = len(cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
        
        # Score based on number of confluence levels
        return min(10, line_count * 2)

    def _analyze_trend_strength(self, image: np.ndarray) -> float:
        """Phase 3: Analyze trend strength (0-10 scale)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect diagonal lines (trend lines)
        edges = cv2.Canny(gray, 50, 150)
        
        # Use Hough transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Analyze line angles to determine trend strength
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if 30 < angle < 150:  # Filter for diagonal lines
                    angles.append(angle)
            
            # Strong trend = consistent diagonal lines
            if angles:
                angle_std = np.std(angles)
                return max(0, 10 - angle_std/10)
        
        return 0

    def _calculate_setup_quality(self, fvg_quality: float, confluence: float, trend: float) -> float:
        """Calculate overall setup quality score"""
        # Weighted average of all factors
        weights = {'fvg': 0.4, 'confluence': 0.3, 'trend': 0.3}
        
        quality = (fvg_quality * weights['fvg'] + 
                  confluence * weights['confluence'] + 
                  trend * weights['trend'])
        
        return round(quality, 1)



# Flask integration
def analyze_trading_screenshot(image_data: str) -> Dict:
    """Main function to be called from Flask"""
    analyzer = ScreenshotAnalyzer()
    return analyzer.analyze_screenshot(image_data)