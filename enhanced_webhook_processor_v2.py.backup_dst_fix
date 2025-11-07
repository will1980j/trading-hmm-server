#!/usr/bin/env python3
"""
🚀 ENHANCED WEBHOOK PROCESSOR V2
Integrates Enhanced FVG signals with Complete Automation Pipeline
"""

import json
import logging
from datetime import datetime
from complete_automation_pipeline import process_signal_through_complete_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWebhookProcessorV2:
    """
    Enhanced webhook processor for V2 automation system
    Handles comprehensive signal data from Enhanced FVG indicator
    """
    
    def __init__(self):
        self.processed_signals = 0
        self.successful_automations = 0
        self.failed_automations = 0
    
    def process_enhanced_fvg_webhook(self, raw_webhook_data):
        """
        Process Enhanced FVG webhook data through complete automation pipeline
        
        Args:
            raw_webhook_data: Raw data from TradingView Enhanced FVG indicator
            
        Returns:
            dict: Processing result with automation status
        """
        try:
            logger.info("🎯 Processing Enhanced FVG Webhook")
            
            # Parse and validate webhook data
            parsed_data = self._parse_webhook_data(raw_webhook_data)
            
            if not parsed_data['valid']:
                logger.warning(f"❌ Invalid webhook data: {parsed_data['reason']}")
                self.failed_automations += 1
                return {
                    'success': False,
                    'error': parsed_data['reason'],
                    'automation_level': 'webhook_validation_failed'
                }
            
            # Extract comprehensive signal data
            signal_data = self._extract_comprehensive_signal_data(parsed_data['data'])
            
            # Process through complete automation pipeline
            automation_result = process_signal_through_complete_pipeline(signal_data)
            
            # Update statistics
            self.processed_signals += 1
            if automation_result['success']:
                self.successful_automations += 1
                logger.info(f"✅ Signal automated successfully - Trade ID: {automation_result.get('trade_id')}")
            else:
                self.failed_automations += 1
                logger.warning(f"❌ Signal automation failed: {automation_result.get('reason', automation_result.get('error'))}")
            
            # Return comprehensive result
            return {
                'success': automation_result['success'],
                'webhook_processing': 'enhanced_v2',
                'automation_result': automation_result,
                'signal_data': signal_data,
                'processing_stats': self._get_processing_stats(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced webhook processing error: {str(e)}")
            self.failed_automations += 1
            return {
                'success': False,
                'error': str(e),
                'webhook_processing': 'enhanced_v2_failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_webhook_data(self, raw_data):
        """Parse and validate raw webhook data"""
        try:
            # Handle different data formats
            if isinstance(raw_data, str):
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    # Handle plain text webhook format
                    data = self._parse_plain_text_webhook(raw_data)
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                return {
                    'valid': False,
                    'reason': f'Unsupported data type: {type(raw_data)}'
                }
            
            # Validate required fields
            validation_result = self._validate_webhook_structure(data)
            
            if validation_result['valid']:
                return {
                    'valid': True,
                    'data': data
                }
            else:
                return validation_result
                
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Parsing error: {str(e)}'
            }
    
    def _parse_plain_text_webhook(self, text_data):
        """Parse plain text webhook format (fallback)"""
        try:
            # Handle legacy format: "SIGNAL:Bullish:4156.25:85.0:1H:Bullish..."
            if text_data.startswith('SIGNAL:'):
                parts = text_data.split(':')
                if len(parts) >= 4:
                    return {
                        'signal_type': parts[1],
                        'price': float(parts[2]),
                        'strength': float(parts[3]) if len(parts) > 3 else 75.0,
                        'session_data': {
                            'current_session': 'NY AM',  # Default
                            'valid': True
                        },
                        'signal_candle': {
                            'close': float(parts[2]),
                            'open': float(parts[2]) - 0.5,
                            'high': float(parts[2]) + 0.5,
                            'low': float(parts[2]) - 0.5
                        },
                        'format': 'legacy_text'
                    }
            
            # Default fallback
            return {
                'signal_type': 'Unknown',
                'format': 'unknown_text',
                'raw_text': text_data
            }
            
        except Exception as e:
            logger.error(f"❌ Plain text parsing error: {str(e)}")
            return {
                'signal_type': 'Unknown',
                'format': 'parse_error',
                'error': str(e)
            }
    
    def _validate_webhook_structure(self, data):
        """Validate webhook data structure"""
        try:
            # Check for signal type
            if 'signal_type' not in data:
                return {
                    'valid': False,
                    'reason': 'Missing signal_type field'
                }
            
            # Validate signal type
            if data['signal_type'] not in ['Bullish', 'Bearish']:
                return {
                    'valid': False,
                    'reason': f'Invalid signal_type: {data["signal_type"]}'
                }
            
            # Check for basic price data
            if 'signal_candle' in data:
                candle = data['signal_candle']
                required_candle_fields = ['open', 'high', 'low', 'close']
                missing_fields = [field for field in required_candle_fields if field not in candle]
                
                if missing_fields:
                    return {
                        'valid': False,
                        'reason': f'Missing candle fields: {missing_fields}'
                    }
            elif 'price' not in data:
                return {
                    'valid': False,
                    'reason': 'Missing both signal_candle and price data'
                }
            
            return {
                'valid': True
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}'
            }
    
    def _extract_comprehensive_signal_data(self, parsed_data):
        """Extract comprehensive signal data for automation pipeline"""
        try:
            # Build comprehensive signal data structure
            signal_data = {
                'signal_type': parsed_data.get('signal_type'),
                'timestamp': datetime.now().isoformat(),
                
                # Signal candle data
                'signal_candle': self._extract_signal_candle_data(parsed_data),
                
                # FVG analysis data
                'fvg_data': self._extract_fvg_data(parsed_data),
                
                # HTF bias data
                'htf_data': self._extract_htf_data(parsed_data),
                
                # Session data
                'session_data': self._extract_session_data(parsed_data),
                
                # Methodology data
                'methodology_data': self._extract_methodology_data(parsed_data),
                
                # Market context
                'market_context': self._extract_market_context(parsed_data),
                
                # Raw webhook data
                'raw_webhook_data': parsed_data
            }
            
            return signal_data
            
        except Exception as e:
            logger.error(f"❌ Signal data extraction error: {str(e)}")
            return {
                'signal_type': parsed_data.get('signal_type', 'Unknown'),
                'error': str(e),
                'raw_data': parsed_data
            }
    
    def _extract_signal_candle_data(self, data):
        """Extract signal candle OHLC data"""
        if 'signal_candle' in data:
            return data['signal_candle']
        elif 'price' in data:
            # Create synthetic candle from single price
            price = float(data['price'])
            return {
                'open': price - 0.25,
                'high': price + 0.25,
                'low': price - 0.25,
                'close': price
            }
        else:
            return {
                'open': None,
                'high': None,
                'low': None,
                'close': None
            }
    
    def _extract_fvg_data(self, data):
        """Extract FVG analysis data"""
        fvg_data = data.get('fvg_data', {})
        
        return {
            'bias': fvg_data.get('bias', data.get('signal_type')),
            'strength': fvg_data.get('strength', data.get('strength', 75.0)),
            'gap_size': fvg_data.get('gap_size'),
            'gap_type': fvg_data.get('gap_type', 'FVG')
        }
    
    def _extract_htf_data(self, data):
        """Extract Higher Timeframe bias data"""
        htf_data = data.get('htf_data', {})
        
        return {
            'aligned': htf_data.get('aligned', True),  # Default to aligned
            'bias_1h': htf_data.get('bias_1h', data.get('signal_type')),
            'bias_15m': htf_data.get('bias_15m', data.get('signal_type')),
            'bias_5m': htf_data.get('bias_5m', data.get('signal_type')),
            'alignment_strength': htf_data.get('alignment_strength', 85.0)
        }
    
    def _extract_session_data(self, data):
        """Extract trading session data"""
        session_data = data.get('session_data', {})
        
        # Determine current session if not provided
        current_session = session_data.get('current_session')
        if not current_session:
            current_session = self._determine_current_session()
        
        return {
            'current_session': current_session,
            'valid': session_data.get('valid', True),
            'session_strength': session_data.get('session_strength', 'medium')
        }
    
    def _extract_methodology_data(self, data):
        """Extract methodology-specific data"""
        methodology_data = data.get('methodology_data', {})
        
        return {
            'requires_confirmation': methodology_data.get('requires_confirmation', True),
            'stop_loss_buffer': methodology_data.get('stop_loss_buffer', 25),
            'confirmation_condition': methodology_data.get('confirmation_condition'),
            'break_even_strategy': methodology_data.get('break_even_strategy', 'BE=1')
        }
    
    def _extract_market_context(self, data):
        """Extract market context data"""
        market_context = data.get('market_context', {})
        
        return {
            'volatility': market_context.get('volatility', 'medium'),
            'trend': market_context.get('trend', 'neutral'),
            'volume': market_context.get('volume', 'normal'),
            'news_impact': market_context.get('news_impact', 'none')
        }
    
    def _determine_current_session(self):
        """Determine current trading session based on time"""
        try:
            from datetime import datetime
            import pytz
            
            # Get current Eastern Time
            eastern = pytz.timezone('US/Eastern')
            et_time = datetime.now(eastern)
            hour = et_time.hour
            minute = et_time.minute
            
            # Session determination (Eastern Time)
            if 20 <= hour <= 23:
                return "ASIA"
            elif 0 <= hour <= 5:
                return "LONDON"
            elif hour == 6 or (hour == 8 and minute <= 29):
                return "NY PRE"
            elif (hour == 8 and minute >= 30) or (9 <= hour <= 11):
                return "NY AM"
            elif hour == 12:
                return "NY LUNCH"
            elif 13 <= hour <= 15:
                return "NY PM"
            else:
                return "CLOSED"
                
        except Exception as e:
            logger.warning(f"⚠️ Session determination error: {str(e)}")
            return "NY AM"  # Default fallback
    
    def _get_processing_stats(self):
        """Get current processing statistics"""
        return {
            'total_processed': self.processed_signals,
            'successful_automations': self.successful_automations,
            'failed_automations': self.failed_automations,
            'success_rate': (self.successful_automations / max(self.processed_signals, 1)) * 100
        }
    
    def get_status_report(self):
        """Get comprehensive status report"""
        return {
            'processor_version': 'enhanced_v2',
            'status': 'active',
            'processing_stats': self._get_processing_stats(),
            'capabilities': [
                'enhanced_fvg_processing',
                'complete_automation_pipeline',
                'exact_methodology_compliance',
                'real_time_confirmation_monitoring',
                'automated_mfe_tracking'
            ],
            'timestamp': datetime.now().isoformat()
        }

# Global webhook processor instance
webhook_processor = EnhancedWebhookProcessorV2()

def process_enhanced_webhook(raw_data):
    """Process enhanced webhook data"""
    global webhook_processor
    return webhook_processor.process_enhanced_fvg_webhook(raw_data)

def get_webhook_processor_status():
    """Get webhook processor status"""
    global webhook_processor
    return webhook_processor.get_status_report()