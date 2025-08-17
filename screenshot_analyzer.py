import cv2
import numpy as np
import pytesseract
import re
from PIL import Image
import base64
import io
import json
from typing import Dict, List, Tuple, Optional

class ScreenshotAnalyzer:
    def __init__(self):
        # Configure Tesseract for cloud deployment
        import os
        if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DYNO'):  # Railway or Heroku
            # Tesseract should be in PATH via Aptfile
            pass
        elif os.name == 'nt':  # Windows local development
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pass
        
        # Price patterns for OCR
        self.price_patterns = [
            r'\d{5}\.\d{2}',  # 23850.25
            r'\d{4}\.\d{2}',  # 2385.25
            r'\d{5}',         # 23850
            r'\d{4}',         # 2385
        ]
        
        # MFE patterns
        self.mfe_patterns = [
            r'MFE:\s*(\d+\.?\d*)[Rr]',  # MFE: 2.5R
            r'(\d+\.?\d*)[Rr]',         # 2.5R
            r'(\d+\.?\d*)\s*[Rr]',      # 2.5 R
        ]

    def analyze_screenshot(self, image_data: str) -> Dict:
        """Main analysis function - processes base64 image"""
        try:
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            
            # Phase 1: OCR Price Extraction
            prices = self._extract_prices(image)
            mfe_values = self._extract_mfe_values(image)
            
            # Phase 2: Pattern Recognition (basic implementation)
            fvg_quality = self._analyze_fvg_quality(image)
            confluence_score = self._detect_confluence(image)
            
            # Phase 3: Market Structure (basic implementation)
            trend_strength = self._analyze_trend_strength(image)
            setup_quality = self._calculate_setup_quality(fvg_quality, confluence_score, trend_strength)
            
            return {
                'status': 'success',
                'prices': prices,
                'mfe_values': mfe_values,
                'fvg_quality': fvg_quality,
                'confluence_score': confluence_score,
                'trend_strength': trend_strength,
                'setup_quality': setup_quality,
                'auto_populated': self._suggest_auto_population(prices, mfe_values)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'prices': {},
                'mfe_values': [],
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

    def _extract_prices(self, image: np.ndarray) -> Dict:
        """Phase 1: Extract price levels using OCR"""
        # Preprocess image for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast for price text
        enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=50)
        
        # OCR extraction
        text = pytesseract.image_to_string(enhanced, config='--psm 6')
        
        # Extract prices using patterns
        prices = {}
        all_prices = []
        
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text)
            all_prices.extend([float(match) for match in matches])
        
        # Sort prices and try to identify levels
        if all_prices:
            all_prices = sorted(set(all_prices))
            
            # Heuristic: assume highest is resistance, lowest is support
            if len(all_prices) >= 2:
                prices['entry'] = all_prices[len(all_prices)//2]  # Middle price as entry
                prices['stop'] = min(all_prices)
                prices['target'] = max(all_prices)
        
        return prices

    def _extract_mfe_values(self, image: np.ndarray) -> List[float]:
        """Extract MFE values from chart labels"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 6')
        
        mfe_values = []
        for pattern in self.mfe_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            mfe_values.extend([float(match) for match in matches])
        
        return sorted(set(mfe_values))

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

    def _suggest_auto_population(self, prices: Dict, mfe_values: List[float]) -> Dict:
        """Suggest which fields can be auto-populated"""
        suggestions = {}
        
        if 'entry' in prices:
            suggestions['entryPrice'] = prices['entry']
        if 'stop' in prices:
            suggestions['stopLoss'] = prices['stop']
        if 'target' in prices:
            suggestions['takeProfit'] = prices['target']
        
        if mfe_values:
            # Suggest highest MFE value
            suggestions['mfeNone'] = max(mfe_values)
        
        return suggestions

# Flask integration
def analyze_trading_screenshot(image_data: str) -> Dict:
    """Main function to be called from Flask"""
    analyzer = ScreenshotAnalyzer()
    return analyzer.analyze_screenshot(image_data)