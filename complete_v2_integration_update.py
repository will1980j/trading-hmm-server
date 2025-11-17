#!/usr/bin/env python3
"""
Complete V2 Integration Update for All Dashboards
=================================================

This script identifies and updates ALL endpoints that need V2 integration
to ensure complete data coverage across the entire platform.

Endpoints to Update:
1. Strategy Comparison - needs V1 + V2 data
2. Time Analysis - needs V1 + V2 data  
3. Trading Data API - needs V1 + V2 data
4. Signal Lab Trades API - needs V2 awareness
5. Any other endpoints querying signal data
"""

import os
import sys
import traceback
from datetime import datetime

def create_v2_strategy_comparison_endpoint():
    """Create V2-enhanced strategy comparison endpoint"""
    
    strategy_code = '''
@app.route('/api/strategy-comparison', methods=['GET'])
@login_required
def get_strategy_comparison():
    """Strategy comparison with V1 + V2 data integration"""
    try:
        if not db_enabled or not db:
            return jsonify({'error': 'Database not available'}), 500
        
        from strategy_evaluator import StrategyEvaluator
        evaluator = StrategyEvaluator(db)
        
        # Get optimal strategy with optional constraints
        constraints = {
            'min_trades': 10,
            'min_expectancy': 0.0
        }
        
        result = evaluator.get_optimal_strategy(constraints)
        
        if 'error' in result:
            return jsonify(result), 404
        
        # V2 ENHANCEMENT: Get combined V1 + V2 data for strategy comparison
        cursor = db.conn.cursor()
        cursor.execute("""
            WITH combined_trades AS (
                -- V1 Data (existing signal_lab_trades)
                SELECT 
                    date, time, session, bias,
                    COALESCE(mfe_none, mfe, 0) as mfe,
                    COALESCE(mfe1, 0) as mfe1,
                    'v1' as source,
                    false as auto_populated,
                    NULL as breakeven_achieved
                FROM signal_lab_trades
                WHERE COALESCE(mfe_none, mfe, 0) > 0
                
                UNION ALL
                
                -- V2 Data (new signal_lab_v2_trades)
                SELECT 
                    date, 
                    time,
                    session,
                    CASE 
                        WHEN bias = 'bullish' THEN 'Bullish'
                        WHEN bias = 'bearish' THEN 'Bearish'
                        ELSE bias
                    END as bias,
                    CASE WHEN final_mfe IS NOT NULL THEN final_mfe ELSE current_mfe END as mfe,
                    CASE 
                        WHEN (CASE WHEN final_mfe IS NOT NULL THEN final_mfe ELSE current_mfe END) >= 1.0 THEN 1.0
                        ELSE 0.0
                    END as mfe1,
                    'v2' as source,
                    auto_populated,
                    breakeven_achieved
                FROM signal_lab_v2_trades
                WHERE COALESCE(final_mfe, current_mfe, 0) > 0
            )
            SELECT 
                date, time, session, bias, 