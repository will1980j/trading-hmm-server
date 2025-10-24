"""
Real-time Prediction Accuracy Tracker
Tracks ML predictions vs actual outcomes for continuous model validation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class PredictionRecord:
    """Individual prediction record"""
    prediction_id: str
    signal_id: int
    timestamp: datetime
    symbol: str
    bias: str
    session: str
    price: float
    
    # ML Prediction data
    predicted_outcome: str  # 'Success' or 'Failure'
    confidence: float
    predicted_mfe: float
    predicted_targets: Dict[str, float]  # {'1R': 0.85, '2R': 0.45, '3R': 0.25}
    
    # Actual outcome data (filled when trade completes)
    actual_outcome: Optional[str] = None
    actual_mfe: Optional[float] = None
    actual_targets_hit: Optional[Dict[str, bool]] = None
    outcome_timestamp: Optional[datetime] = None
    
    # Accuracy metrics
    prediction_correct: Optional[bool] = None
    mfe_error: Optional[float] = None
    target_accuracy: Optional[Dict[str, bool]] = None

class PredictionAccuracyTracker:
    """Tracks and analyzes ML prediction accuracy in real-time"""
    
    def __init__(self, db, socketio=None):
        self.db = db
        self.socketio = socketio
        self.active_predictions = {}  # prediction_id -> PredictionRecord
        self.completed_predictions = []
        self.accuracy_stats = {
            'total_predictions': 0,
            'completed_predictions': 0,
            'correct_predictions': 0,
            'overall_accuracy': 0.0,
            'confidence_brackets': {
                'high': {'correct': 0, 'total': 0, 'accuracy': 0.0},  # >80%
                'medium': {'correct': 0, 'total': 0, 'accuracy': 0.0},  # 60-80%
                'low': {'correct': 0, 'total': 0, 'accuracy': 0.0}  # <60%
            },
            'session_accuracy': {},
            'target_accuracy': {'1R': 0.0, '2R': 0.0, '3R': 0.0},
            'mfe_accuracy': {'mean_error': 0.0, 'rmse': 0.0}
        }
        
        # Initialize database table
        self._init_database()
        
        # Load existing predictions
        self._load_active_predictions()
        
        # Start background monitoring
        self._start_monitoring()
    
    def _init_database(self):
        """Initialize prediction tracking table"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_accuracy_tracking (
                    id SERIAL PRIMARY KEY,
                    prediction_id VARCHAR(50) UNIQUE NOT NULL,
                    signal_id INTEGER REFERENCES live_signals(id),
                    timestamp TIMESTAMP NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    bias VARCHAR(20) NOT NULL,
                    session VARCHAR(50) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    
                    -- ML Prediction data
                    predicted_outcome VARCHAR(20) NOT NULL,
                    confidence DECIMAL(5,2) NOT NULL,
                    predicted_mfe DECIMAL(8,4),
                    predicted_targets JSONB,
                    
                    -- Actual outcome data
                    actual_outcome VARCHAR(20),
                    actual_mfe DECIMAL(8,4),
                    actual_targets_hit JSONB,
                    outcome_timestamp TIMESTAMP,
                    
                    -- Accuracy metrics
                    prediction_correct BOOLEAN,
                    mfe_error DECIMAL(8,4),
                    target_accuracy JSONB,
                    
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_tracking_timestamp 
                ON prediction_accuracy_tracking(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_tracking_signal_id 
                ON prediction_accuracy_tracking(signal_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_tracking_session 
                ON prediction_accuracy_tracking(session)
            """)
            
            self.db.conn.commit()
            logger.info("✅ Prediction accuracy tracking table initialized")
            
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error initializing prediction tracking table: {e}")
    
    def record_prediction(self, signal_id: int, signal_data: Dict, ml_prediction: Dict) -> str:
        """Record a new ML prediction for tracking"""
        try:
            prediction_id = f"pred_{signal_id}_{int(time.time())}"
            
            # Create prediction record
            record = PredictionRecord(
                prediction_id=prediction_id,
                signal_id=signal_id,
                timestamp=datetime.now(),
                symbol=signal_data.get('symbol', 'Unknown'),
                bias=signal_data.get('bias', 'Unknown'),
                session=signal_data.get('session', 'Unknown'),
                price=signal_data.get('price', 0.0),
                predicted_outcome=ml_prediction.get('prediction', 'Unknown'),
                confidence=ml_prediction.get('confidence', 0.0),
                predicted_mfe=ml_prediction.get('predicted_mfe', 0.0),
                predicted_targets=ml_prediction.get('multi_target_predictions', {})
            )
            
            # Store in database
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO prediction_accuracy_tracking 
                (prediction_id, signal_id, timestamp, symbol, bias, session, price,
                 predicted_outcome, confidence, predicted_mfe, predicted_targets)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                record.prediction_id, record.signal_id, record.timestamp,
                record.symbol, record.bias, record.session, record.price,
                record.predicted_outcome, record.confidence, record.predicted_mfe,
                json.dumps(record.predicted_targets)
            ))
            
            self.db.conn.commit()
            
            # Add to active predictions
            self.active_predictions[prediction_id] = record
            self.accuracy_stats['total_predictions'] += 1
            
            logger.info(f"📊 Prediction recorded: {prediction_id} - {record.predicted_outcome} ({record.confidence}%)")
            
            # Broadcast to WebSocket clients
            if self.socketio:
                self.socketio.emit('prediction_recorded', {
                    'prediction_id': prediction_id,
                    'signal_id': signal_id,
                    'prediction': record.predicted_outcome,
                    'confidence': record.confidence,
                    'timestamp': record.timestamp.isoformat()
                })
            
            return prediction_id
            
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error recording prediction: {e}")
            return None
    
    def update_actual_outcome(self, signal_id: int, actual_data: Dict):
        """Update prediction with actual trade outcome"""
        try:
            # Find prediction by signal_id
            prediction_record = None
            for pred_id, record in self.active_predictions.items():
                if record.signal_id == signal_id:
                    prediction_record = record
                    break
            
            if not prediction_record:
                logger.warning(f"No active prediction found for signal_id: {signal_id}")
                return
            
            # Update with actual outcome
            prediction_record.actual_outcome = actual_data.get('outcome', 'Unknown')
            prediction_record.actual_mfe = actual_data.get('mfe', 0.0)
            prediction_record.actual_targets_hit = actual_data.get('targets_hit', {})
            prediction_record.outcome_timestamp = datetime.now()
            
            # Calculate accuracy metrics
            prediction_record.prediction_correct = (
                prediction_record.predicted_outcome.lower() == 
                prediction_record.actual_outcome.lower()
            )
            
            if prediction_record.actual_mfe is not None:
                prediction_record.mfe_error = abs(
                    prediction_record.predicted_mfe - prediction_record.actual_mfe
                )
            
            # Calculate target accuracy
            if prediction_record.actual_targets_hit:
                target_accuracy = {}
                for target, predicted_prob in prediction_record.predicted_targets.items():
                    actual_hit = prediction_record.actual_targets_hit.get(target, False)
                    # Consider prediction correct if high probability (>0.5) and hit, or low probability and missed
                    target_accuracy[target] = (
                        (predicted_prob > 0.5 and actual_hit) or 
                        (predicted_prob <= 0.5 and not actual_hit)
                    )
                prediction_record.target_accuracy = target_accuracy
            
            # Update database
            cursor = self.db.conn.cursor()
            cursor.execute("""
                UPDATE prediction_accuracy_tracking 
                SET actual_outcome = %s, actual_mfe = %s, actual_targets_hit = %s,
                    outcome_timestamp = %s, prediction_correct = %s, mfe_error = %s,
                    target_accuracy = %s, updated_at = NOW()
                WHERE prediction_id = %s
            """, (
                prediction_record.actual_outcome,
                prediction_record.actual_mfe,
                json.dumps(prediction_record.actual_targets_hit),
                prediction_record.outcome_timestamp,
                prediction_record.prediction_correct,
                prediction_record.mfe_error,
                json.dumps(prediction_record.target_accuracy),
                prediction_record.prediction_id
            ))
            
            self.db.conn.commit()
            
            # Move to completed predictions
            self.completed_predictions.append(prediction_record)
            del self.active_predictions[prediction_record.prediction_id]
            
            # Update accuracy stats
            self._update_accuracy_stats()
            
            logger.info(f"✅ Prediction outcome updated: {prediction_record.prediction_id} - "
                       f"Correct: {prediction_record.prediction_correct}")
            
            # Broadcast update
            if self.socketio:
                self.socketio.emit('prediction_outcome_updated', {
                    'prediction_id': prediction_record.prediction_id,
                    'signal_id': signal_id,
                    'predicted': prediction_record.predicted_outcome,
                    'actual': prediction_record.actual_outcome,
                    'correct': prediction_record.prediction_correct,
                    'confidence': prediction_record.confidence,
                    'mfe_error': prediction_record.mfe_error,
                    'timestamp': prediction_record.outcome_timestamp.isoformat()
                })
            
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error updating prediction outcome: {e}")
    
    def _update_accuracy_stats(self):
        """Update overall accuracy statistics"""
        try:
            # Get recent completed predictions (last 100)
            recent_predictions = self.completed_predictions[-100:]
            
            if not recent_predictions:
                return
            
            # Overall accuracy
            correct_predictions = sum(1 for p in recent_predictions if p.prediction_correct)
            self.accuracy_stats['completed_predictions'] = len(recent_predictions)
            self.accuracy_stats['correct_predictions'] = correct_predictions
            self.accuracy_stats['overall_accuracy'] = (
                correct_predictions / len(recent_predictions) * 100
            )
            
            # Confidence bracket accuracy
            for bracket in ['high', 'medium', 'low']:
                self.accuracy_stats['confidence_brackets'][bracket] = {
                    'correct': 0, 'total': 0, 'accuracy': 0.0
                }
            
            for pred in recent_predictions:
                if pred.confidence >= 80:
                    bracket = 'high'
                elif pred.confidence >= 60:
                    bracket = 'medium'
                else:
                    bracket = 'low'
                
                self.accuracy_stats['confidence_brackets'][bracket]['total'] += 1
                if pred.prediction_correct:
                    self.accuracy_stats['confidence_brackets'][bracket]['correct'] += 1
            
            # Calculate bracket accuracies
            for bracket_data in self.accuracy_stats['confidence_brackets'].values():
                if bracket_data['total'] > 0:
                    bracket_data['accuracy'] = (
                        bracket_data['correct'] / bracket_data['total'] * 100
                    )
            
            # Session accuracy
            session_stats = {}
            for pred in recent_predictions:
                if pred.session not in session_stats:
                    session_stats[pred.session] = {'correct': 0, 'total': 0}
                session_stats[pred.session]['total'] += 1
                if pred.prediction_correct:
                    session_stats[pred.session]['correct'] += 1
            
            for session, stats in session_stats.items():
                self.accuracy_stats['session_accuracy'][session] = (
                    stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
                )
            
            # Target accuracy
            target_stats = {'1R': [], '2R': [], '3R': []}
            for pred in recent_predictions:
                if pred.target_accuracy:
                    for target, correct in pred.target_accuracy.items():
                        if target in target_stats:
                            target_stats[target].append(correct)
            
            for target, results in target_stats.items():
                if results:
                    self.accuracy_stats['target_accuracy'][target] = (
                        sum(results) / len(results) * 100
                    )
            
            # MFE accuracy
            mfe_errors = [p.mfe_error for p in recent_predictions if p.mfe_error is not None]
            if mfe_errors:
                self.accuracy_stats['mfe_accuracy']['mean_error'] = sum(mfe_errors) / len(mfe_errors)
                self.accuracy_stats['mfe_accuracy']['rmse'] = (
                    sum(e**2 for e in mfe_errors) / len(mfe_errors)
                ) ** 0.5
            
            # Broadcast updated stats
            if self.socketio:
                self.socketio.emit('accuracy_stats_updated', {
                    'stats': self.accuracy_stats,
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error updating accuracy stats: {e}")
    
    def _load_active_predictions(self):
        """Load active predictions from database on startup"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT * FROM prediction_accuracy_tracking 
                WHERE actual_outcome IS NULL 
                AND timestamp > NOW() - INTERVAL '24 hours'
                ORDER BY timestamp DESC
            """)
            
            for row in cursor.fetchall():
                record = PredictionRecord(
                    prediction_id=row['prediction_id'],
                    signal_id=row['signal_id'],
                    timestamp=row['timestamp'],
                    symbol=row['symbol'],
                    bias=row['bias'],
                    session=row['session'],
                    price=float(row['price']),
                    predicted_outcome=row['predicted_outcome'],
                    confidence=float(row['confidence']),
                    predicted_mfe=float(row['predicted_mfe']) if row['predicted_mfe'] else 0.0,
                    predicted_targets=json.loads(row['predicted_targets']) if row['predicted_targets'] else {}
                )
                
                self.active_predictions[record.prediction_id] = record
            
            logger.info(f"📊 Loaded {len(self.active_predictions)} active predictions")
            
        except Exception as e:
            logger.error(f"Error loading active predictions: {e}")
    
    def _start_monitoring(self):
        """Start background monitoring for stale predictions"""
        def monitor():
            while True:
                try:
                    # Check for stale predictions (>4 hours old)
                    stale_cutoff = datetime.now() - timedelta(hours=4)
                    stale_predictions = [
                        pred_id for pred_id, record in self.active_predictions.items()
                        if record.timestamp < stale_cutoff
                    ]
                    
                    for pred_id in stale_predictions:
                        logger.warning(f"⚠️ Stale prediction detected: {pred_id}")
                        # Could auto-mark as 'timeout' or investigate further
                    
                    # Update stats periodically
                    self._update_accuracy_stats()
                    
                    time.sleep(300)  # Check every 5 minutes
                    
                except Exception as e:
                    logger.error(f"Error in prediction monitoring: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("✅ Prediction accuracy monitoring started")
    
    def get_accuracy_report(self) -> Dict:
        """Get comprehensive accuracy report"""
        return {
            'summary': self.accuracy_stats,
            'active_predictions': len(self.active_predictions),
            'recent_predictions': [
                {
                    'prediction_id': p.prediction_id,
                    'symbol': p.symbol,
                    'bias': p.bias,
                    'predicted': p.predicted_outcome,
                    'confidence': p.confidence,
                    'timestamp': p.timestamp.isoformat()
                }
                for p in list(self.active_predictions.values())[-10:]
            ],
            'completed_predictions': [
                {
                    'prediction_id': p.prediction_id,
                    'symbol': p.symbol,
                    'bias': p.bias,
                    'predicted': p.predicted_outcome,
                    'actual': p.actual_outcome,
                    'correct': p.prediction_correct,
                    'confidence': p.confidence,
                    'mfe_error': p.mfe_error,
                    'timestamp': p.timestamp.isoformat()
                }
                for p in self.completed_predictions[-10:]
            ]
        }