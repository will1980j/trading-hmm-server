import json
from datetime import datetime, timedelta
from database.railway_db import RailwayDB
from news_api import get_real_nq_levels
import requests

class LevelTracker:
    def __init__(self):
        self.db = RailwayDB()
        self.setup_tables()
    
    def setup_tables(self):
        """Create tables for level tracking"""
        cursor = self.db.conn.cursor()
        
        # Daily levels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_levels (
                id SERIAL PRIMARY KEY,
                date DATE UNIQUE,
                support_levels JSON,
                resistance_levels JSON,
                pivot_level DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level hits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_hits (
                id SERIAL PRIMARY KEY,
                date DATE,
                level_type VARCHAR(20),
                predicted_level DECIMAL(10,2),
                actual_hit BOOLEAN,
                hit_time TIME,
                price_at_hit DECIMAL(10,2),
                distance_from_level DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level accuracy summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_accuracy (
                id SERIAL PRIMARY KEY,
                level_type VARCHAR(20),
                total_predictions INTEGER,
                total_hits INTEGER,
                accuracy_percentage DECIMAL(5,2),
                confidence_score DECIMAL(5,2),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db.conn.commit()
    
    def capture_daily_levels(self, ai_levels=None):
        """Capture and store today's predicted levels from AI analysis"""
        today = datetime.now().date()
        
        if ai_levels:
            # Use AI-generated levels
            levels = ai_levels
        else:
            # Fallback to basic technical levels
            levels = get_real_nq_levels()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            INSERT INTO daily_levels (date, support_levels, resistance_levels, pivot_level)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET
                support_levels = EXCLUDED.support_levels,
                resistance_levels = EXCLUDED.resistance_levels,
                pivot_level = EXCLUDED.pivot_level
        """, (
            today,
            json.dumps(levels.get('support', [])),
            json.dumps(levels.get('resistance', [])),
            levels.get('pivot', 0)
        ))
        
        self.db.conn.commit()
        return levels
    
    def parse_ai_levels(self, ai_analysis_text):
        """Parse AI market analysis to extract specific levels"""
        import re
        
        levels = {
            'support': [],
            'resistance': [],
            'pivot': 0,
            'session_highs': [],
            'session_lows': [],
            'fvg_zones': []
        }
        
        # Extract price levels using regex
        price_pattern = r'(\d{5}(?:\.\d{1,2})?)'  # Matches 5-digit prices like 23850
        
        lines = ai_analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Identify sections
            if 'session high' in line_lower or 'recent high' in line_lower:
                current_section = 'session_highs'
            elif 'session low' in line_lower or 'recent low' in line_lower:
                current_section = 'session_lows'
            elif 'pivot' in line_lower:
                current_section = 'pivot'
            elif 'fvg' in line_lower and ('gap' in line_lower or 'zone' in line_lower):
                current_section = 'fvg_zones'
            elif 'resistance' in line_lower:
                current_section = 'resistance'
            elif 'support' in line_lower:
                current_section = 'support'
            
            # Extract prices from current line
            prices = re.findall(price_pattern, line)
            
            for price_str in prices:
                price = float(price_str)
                if 20000 <= price <= 30000:  # Valid NQ range
                    if current_section == 'session_highs':
                        levels['session_highs'].append(price)
                        levels['resistance'].append(price)
                    elif current_section == 'session_lows':
                        levels['session_lows'].append(price)
                        levels['support'].append(price)
                    elif current_section == 'pivot':
                        levels['pivot'] = price
                    elif current_section == 'fvg_zones':
                        levels['fvg_zones'].append(price)
                    elif current_section == 'resistance':
                        levels['resistance'].append(price)
                    elif current_section == 'support':
                        levels['support'].append(price)
        
        # Remove duplicates and sort
        levels['support'] = sorted(list(set(levels['support'])))
        levels['resistance'] = sorted(list(set(levels['resistance'])), reverse=True)
        levels['session_highs'] = sorted(list(set(levels['session_highs'])), reverse=True)
        levels['session_lows'] = sorted(list(set(levels['session_lows'])))
        levels['fvg_zones'] = sorted(list(set(levels['fvg_zones'])))
        
        return levels
    
    def check_level_hits(self, date=None):
        """Check if levels were hit on given date"""
        if not date:
            date = datetime.now().date()
        
        # Get NQ price data for the day
        nq_data = self.get_nq_daily_data(date)
        if not nq_data:
            return
        
        # Get predicted levels for that date
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM daily_levels WHERE date = %s", (date,))
        level_data = cursor.fetchone()
        
        if not level_data:
            return
        
        support_levels = json.loads(level_data[2])
        resistance_levels = json.loads(level_data[3])
        pivot_level = float(level_data[4])
        
        # Check hits
        self.analyze_level_hits(date, nq_data, support_levels, resistance_levels, pivot_level)
    
    def get_nq_daily_data(self, date):
        """Get NQ OHLC data for specific date"""
        try:
            # Yahoo Finance API for historical data
            end_date = date + timedelta(days=1)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/NQ=F?period1={int(date.timestamp())}&period2={int(end_date.timestamp())}&interval=5m"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get('chart', {}).get('result', [])
                
                if result:
                    quote = result[0]
                    indicators = quote.get('indicators', {}).get('quote', [{}])[0]
                    
                    return {
                        'high': max([h for h in indicators.get('high', []) if h]),
                        'low': min([l for l in indicators.get('low', []) if l]),
                        'open': indicators.get('open', [None])[0],
                        'close': indicators.get('close', [])[-1]
                    }
        except Exception as e:
            print(f"Error getting NQ data: {e}")
        
        return None
    
    def analyze_level_hits(self, date, price_data, support_levels, resistance_levels, pivot_level):
        """Analyze which levels were hit with ICT-specific logic"""
        day_high = price_data['high']
        day_low = price_data['low']
        
        cursor = self.db.conn.cursor()
        
        # ICT-specific hit detection (within 5 points for liquidity sweeps)
        hit_tolerance = 5.0
        
        # Check support levels (liquidity sweeps below)
        for level in support_levels:
            # Hit if price swept below or touched within tolerance
            hit = (day_low <= level + hit_tolerance) and (day_low >= level - hit_tolerance)
            distance = min(abs(day_high - level), abs(day_low - level))
            
            cursor.execute("""
                INSERT INTO level_hits (date, level_type, predicted_level, actual_hit, distance_from_level)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date, level_type, predicted_level) DO UPDATE SET
                    actual_hit = EXCLUDED.actual_hit,
                    distance_from_level = EXCLUDED.distance_from_level
            """, (date, 'support', level, hit, distance))
        
        # Check resistance levels (liquidity sweeps above)
        for level in resistance_levels:
            hit = (day_high >= level - hit_tolerance) and (day_high <= level + hit_tolerance)
            distance = min(abs(day_high - level), abs(day_low - level))
            
            cursor.execute("""
                INSERT INTO level_hits (date, level_type, predicted_level, actual_hit, distance_from_level)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date, level_type, predicted_level) DO UPDATE SET
                    actual_hit = EXCLUDED.actual_hit,
                    distance_from_level = EXCLUDED.distance_from_level
            """, (date, 'resistance', level, hit, distance))
        
        # Check pivot (exact touch within tolerance)
        if pivot_level > 0:
            hit = day_low <= pivot_level <= day_high
            distance = min(abs(day_high - pivot_level), abs(day_low - pivot_level))
            
            cursor.execute("""
                INSERT INTO level_hits (date, level_type, predicted_level, actual_hit, distance_from_level)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date, level_type, predicted_level) DO UPDATE SET
                    actual_hit = EXCLUDED.actual_hit,
                    distance_from_level = EXCLUDED.distance_from_level
            """, (date, 'pivot', pivot_level, hit, distance))
        
        self.db.conn.commit()
    
    def update_accuracy_scores(self):
        """Update accuracy scores for all level types"""
        cursor = self.db.conn.cursor()
        
        for level_type in ['support', 'resistance', 'pivot']:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN actual_hit THEN 1 ELSE 0 END) as hits
                FROM level_hits 
                WHERE level_type = %s
            """, (level_type,))
            
            result = cursor.fetchone()
            total, hits = result[0], result[1]
            
            if total > 0:
                accuracy = (hits / total) * 100
                confidence = self.calculate_confidence_score(level_type, accuracy, total)
                
                cursor.execute("""
                    INSERT INTO level_accuracy (level_type, total_predictions, total_hits, accuracy_percentage, confidence_score)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (level_type) DO UPDATE SET
                        total_predictions = EXCLUDED.total_predictions,
                        total_hits = EXCLUDED.total_hits,
                        accuracy_percentage = EXCLUDED.accuracy_percentage,
                        confidence_score = EXCLUDED.confidence_score,
                        last_updated = CURRENT_TIMESTAMP
                """, (level_type, total, hits, accuracy, confidence))
        
        self.db.conn.commit()
    
    def calculate_confidence_score(self, level_type, accuracy, sample_size):
        """Calculate confidence score based on accuracy and sample size"""
        # Base confidence on accuracy
        base_confidence = accuracy
        
        # Adjust for sample size (more data = higher confidence)
        sample_factor = min(sample_size / 30, 1.0)  # Max confidence at 30+ samples
        
        # Adjust for level type reliability (resistance typically more reliable)
        type_factor = 1.1 if level_type == 'resistance' else 1.0
        
        confidence = base_confidence * sample_factor * type_factor
        return min(confidence, 100.0)
    
    def get_accuracy_report(self):
        """Get current accuracy report"""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM level_accuracy ORDER BY confidence_score DESC")
        return cursor.fetchall()

# Daily automation function
def run_daily_level_tracking():
    """Run daily level tracking process"""
    tracker = LevelTracker()
    
    # Capture today's levels
    levels = tracker.capture_daily_levels()
    print(f"Captured levels: {levels}")
    
    # Check yesterday's level hits
    yesterday = datetime.now().date() - timedelta(days=1)
    tracker.check_level_hits(yesterday)
    
    # Update accuracy scores
    tracker.update_accuracy_scores()
    
    return tracker.get_accuracy_report()