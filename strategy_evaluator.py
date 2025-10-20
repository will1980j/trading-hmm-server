"""
Unified Strategy Evaluation Framework
Consolidates: Time Analysis, ML Predictions, Session Performance, Risk Metrics
"""
from typing import Dict, List, Tuple
import math

class StrategyEvaluator:
    def __init__(self, db):
        self.db = db
        
    def evaluate_strategy(self, strategy: Dict) -> Dict:
        """
        Evaluate a strategy across all dimensions
        Returns weighted score + breakdown
        """
        scores = {
            'expectancy': self._score_expectancy(strategy),
            'risk_adjusted': self._score_risk_adjusted(strategy),
            'consistency': self._score_consistency(strategy),
            'drawdown': self._score_drawdown(strategy),
            'sample_size': self._score_sample_size(strategy)
        }
        
        # Weighted composite score
        weights = {
            'expectancy': 0.30,
            'risk_adjusted': 0.25,
            'consistency': 0.20,
            'drawdown': 0.15,
            'sample_size': 0.10
        }
        
        composite = sum(scores[k] * weights[k] for k in weights)
        
        return {
            'composite_score': composite,
            'scores': scores,
            'weights': weights,
            'metrics': self._calculate_metrics(strategy),
            'recommendation': self._get_recommendation(composite, scores)
        }
    
    def _score_expectancy(self, strategy: Dict) -> float:
        """Score based on expectancy (0-100)"""
        exp = strategy.get('expectancy', 0)
        if exp <= 0:
            return 0
        # 0.5R = 100, scales down from there
        return min(100, (exp / 0.5) * 100)
    
    def _score_risk_adjusted(self, strategy: Dict) -> float:
        """Sharpe-like ratio score"""
        exp = strategy.get('expectancy', 0)
        std = strategy.get('std_dev', 1)
        if std == 0:
            return 0
        sharpe = exp / std
        return min(100, max(0, (sharpe + 1) * 50))
    
    def _score_consistency(self, strategy: Dict) -> float:
        """Score based on win rate and profit factor"""
        wr = strategy.get('win_rate', 0)
        pf = strategy.get('profit_factor', 0)
        
        wr_score = wr * 100
        pf_score = min(100, (pf / 2.0) * 100) if pf > 0 else 0
        
        return (wr_score * 0.6) + (pf_score * 0.4)
    
    def _score_drawdown(self, strategy: Dict) -> float:
        """Lower drawdown = higher score"""
        dd = strategy.get('max_drawdown', 0)
        if dd == 0:
            return 100
        # 5R drawdown = 50 score, scales inversely
        return max(0, 100 - (dd / 5.0) * 50)
    
    def _score_sample_size(self, strategy: Dict) -> float:
        """Confidence based on sample size"""
        n = strategy.get('total_trades', 0)
        if n < 30:
            return (n / 30) * 50
        elif n < 100:
            return 50 + ((n - 30) / 70) * 30
        else:
            return min(100, 80 + ((n - 100) / 100) * 20)
    
    def _calculate_metrics(self, strategy: Dict) -> Dict:
        """Calculate key trading metrics"""
        exp = strategy.get('expectancy', 0)
        wr = strategy.get('win_rate', 0)
        total = strategy.get('total_trades', 0)
        
        return {
            'expectancy': round(exp, 3),
            'win_rate': round(wr * 100, 1),
            'profit_factor': round(strategy.get('profit_factor', 0), 2),
            'sharpe_ratio': round(exp / strategy.get('std_dev', 1), 2),
            'total_trades': total,
            'avg_r_per_trade': round(strategy.get('total_r', 0) / total, 2) if total > 0 else 0
        }
    
    def _get_recommendation(self, composite: float, scores: Dict) -> str:
        """Generate actionable recommendation"""
        if composite >= 80:
            return "TRADE - Strong edge across all metrics"
        elif composite >= 65:
            return "TRADE WITH CAUTION - Good edge but monitor weak areas"
        elif composite >= 50:
            return "PAPER TRADE - Potential edge needs validation"
        else:
            return "AVOID - Insufficient edge or high risk"
    
    def compare_strategies(self, strategies: List[Dict]) -> List[Dict]:
        """Compare multiple strategies and rank them"""
        evaluated = []
        for strategy in strategies:
            eval_result = self.evaluate_strategy(strategy)
            eval_result['strategy'] = strategy
            evaluated.append(eval_result)
        
        # Sort by composite score
        evaluated.sort(key=lambda x: x['composite_score'], reverse=True)
        return evaluated
    
    def get_optimal_strategy(self, constraints: Dict = None) -> Dict:
        """
        Find optimal strategy from database given constraints
        Constraints: min_win_rate, max_drawdown, min_trades, etc.
        """
        cursor = self.db.conn.cursor()
        
        # Get all completed trades
        cursor.execute("""
            SELECT date, time, session, bias,
                   COALESCE(mfe_none, mfe, 0) as mfe_none,
                   COALESCE(mfe1, 0) as mfe1
            FROM signal_lab_trades
        """)
        
        trades = cursor.fetchall()
        
        if not trades:
            return {'error': 'No trade data available'}
        
        # Test different strategy combinations
        strategies = self._generate_strategy_combinations(trades)
        
        # Apply constraints
        if constraints:
            strategies = self._apply_constraints(strategies, constraints)
        
        # Evaluate and rank
        evaluated = self.compare_strategies(strategies)
        
        return evaluated[0] if evaluated else {'error': 'No strategies meet constraints'}
    
    def _generate_strategy_combinations(self, trades: List) -> List[Dict]:
        """Generate strategy combinations to test"""
        strategies = []
        
        sessions = ['Asia', 'London', 'NY Pre Market', 'NY AM', 'NY Lunch', 'NY PM']
        be_strategies = ['none', 'be1']
        r_targets = [1.0, 1.5, 2.0, 2.5, 3.0]
        
        for session in sessions:
            for be_strat in be_strategies:
                for r_target in r_targets:
                    strategy = self._test_strategy(trades, session, be_strat, r_target)
                    if strategy['total_trades'] >= 10:  # Minimum sample
                        strategies.append(strategy)
        
        return strategies
    
    def _test_strategy(self, trades: List, session: str, be_strategy: str, r_target: float) -> Dict:
        """Test a specific strategy configuration"""
        session_trades = [t for t in trades if t['session'] == session]
        
        results = []
        for trade in session_trades:
            if be_strategy == 'none':
                mfe = trade['mfe_none']
                if mfe < 0:
                    result = -1
                elif mfe >= r_target:
                    result = r_target
                else:
                    result = -1
            else:  # be1
                mfe1 = trade['mfe1']
                if mfe1 < 1:
                    result = -1
                elif mfe1 >= r_target:
                    result = r_target
                else:
                    result = 0  # Hit BE but not target
            
            results.append(result)
        
        if not results:
            return {'total_trades': 0}
        
        wins = [r for r in results if r > 0]
        losses = [r for r in results if r < 0]
        
        total_r = sum(results)
        expectancy = total_r / len(results)
        win_rate = len(wins) / len(results)
        
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Calculate standard deviation
        mean = expectancy
        variance = sum((r - mean) ** 2 for r in results) / len(results)
        std_dev = math.sqrt(variance)
        
        # Calculate max drawdown
        peak = 0
        max_dd = 0
        running = 0
        for r in results:
            running += r
            if running > peak:
                peak = running
            dd = peak - running
            if dd > max_dd:
                max_dd = dd
        
        return {
            'session': session,
            'be_strategy': be_strategy,
            'r_target': r_target,
            'expectancy': expectancy,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_r': total_r,
            'total_trades': len(results),
            'std_dev': std_dev,
            'max_drawdown': max_dd
        }
    
    def _apply_constraints(self, strategies: List[Dict], constraints: Dict) -> List[Dict]:
        """Filter strategies by constraints"""
        filtered = []
        
        for strategy in strategies:
            if constraints.get('min_win_rate') and strategy['win_rate'] < constraints['min_win_rate']:
                continue
            if constraints.get('max_drawdown') and strategy['max_drawdown'] > constraints['max_drawdown']:
                continue
            if constraints.get('min_trades') and strategy['total_trades'] < constraints['min_trades']:
                continue
            if constraints.get('min_expectancy') and strategy['expectancy'] < constraints['min_expectancy']:
                continue
            
            filtered.append(strategy)
        
        return filtered
