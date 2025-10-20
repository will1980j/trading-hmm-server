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
        Evaluate a strategy for 1m scalping
        Focus: Profit Factor, Drawdown, Omega, Sortino, Calmar
        """
        scores = {
            'expectancy': self._score_expectancy(strategy),
            'profit_factor': self._score_profit_factor(strategy),
            'drawdown': self._score_drawdown(strategy),
            'omega': self._score_omega(strategy),
            'sortino': self._score_sortino(strategy)
        }
        
        # Weighted for scalping
        weights = {
            'expectancy': 0.25,
            'profit_factor': 0.25,
            'drawdown': 0.20,
            'omega': 0.15,
            'sortino': 0.15
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
    
    def _score_profit_factor(self, strategy: Dict) -> float:
        """PF: 2.0+ = excellent for scalping"""
        pf = strategy.get('profit_factor', 0)
        if pf <= 1.0:
            return 0
        return min(100, ((pf - 1.0) / 1.5) * 100)
    
    def _score_omega(self, strategy: Dict) -> float:
        """Omega ratio: probability-weighted gains/losses"""
        omega = strategy.get('omega_ratio', 0)
        if omega <= 1.0:
            return 0
        return min(100, ((omega - 1.0) / 1.0) * 100)
    
    def _score_sortino(self, strategy: Dict) -> float:
        """Sortino: downside deviation focus"""
        sortino = strategy.get('sortino_ratio', 0)
        if sortino <= 0:
            return 0
        return min(100, (sortino / 2.0) * 100)
    
    def _score_drawdown(self, strategy: Dict) -> float:
        """Lower drawdown = higher score"""
        dd = strategy.get('max_drawdown', 0)
        if dd == 0:
            return 100
        # 5R drawdown = 50 score, scales inversely
        return max(0, 100 - (dd / 5.0) * 50)
    

    
    def _calculate_metrics(self, strategy: Dict) -> Dict:
        """Calculate scalping-focused metrics"""
        exp = strategy.get('expectancy', 0)
        wr = strategy.get('win_rate', 0)
        total = strategy.get('total_trades', 0)
        dd = strategy.get('max_drawdown', 0.01)
        
        return {
            'expectancy': round(exp, 3),
            'win_rate': round(wr * 100, 1),
            'profit_factor': round(strategy.get('profit_factor', 0), 2),
            'omega_ratio': round(strategy.get('omega_ratio', 0), 2),
            'sortino_ratio': round(strategy.get('sortino_ratio', 0), 2),
            'calmar_ratio': round(strategy.get('total_r', 0) / dd, 2) if dd > 0 else 0,
            'max_drawdown': round(dd, 2),
            'total_trades': total
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
        """Generate ALL strategy combinations: sessions, time windows, macro, BE, R-targets"""
        strategies = []
        
        sessions = ['Asia', 'London', 'NY Pre Market', 'NY AM', 'NY Lunch', 'NY PM']
        be_strategies = ['none', 'be1']
        r_targets = [i * 0.5 for i in range(1, 41)]  # 0.5R to 20R in 0.5R increments
        time_filters = ['all', 'optimal', 'macro']  # all hours, optimal hour per session, macro windows only
        
        # Get optimal hours per session
        optimal_hours = self._find_optimal_hours(trades, sessions)
        
        # All session combinations (1, 2, 3, 4, 5, 6 sessions)
        all_session_combos = []
        for r in range(1, len(sessions) + 1):
            from itertools import combinations
            all_session_combos.extend(['+'.join(combo) for combo in combinations(sessions, r)])
        
        # Test every combination
        for session_combo in all_session_combos:
            for time_filter in time_filters:
                for be_strat in be_strategies:
                    for r_target in r_targets:
                        strategy = self._test_strategy(trades, session_combo, be_strat, r_target, time_filter, optimal_hours)
                        if strategy['total_trades'] >= 10:
                            strategies.append(strategy)
        
        return strategies
    
    def _find_optimal_hours(self, trades: List, sessions: List[str]) -> Dict:
        """Find best hour per session based on raw expectancy"""
        optimal = {}
        for session in sessions:
            session_trades = [t for t in trades if t['session'] == session]
            hourly = {}
            for trade in session_trades:
                if not trade.get('time'):
                    continue
                hour = int(trade['time'].split(':')[0])
                if hour not in hourly:
                    hourly[hour] = []
                hourly[hour].append(trade['mfe_none'])
            
            best_hour = None
            best_exp = -999
            for hour, mfes in hourly.items():
                if len(mfes) < 5:
                    continue
                exp = sum(mfes) / len(mfes)
                if exp > best_exp:
                    best_exp = exp
                    best_hour = hour
            
            if best_hour is not None:
                optimal[session] = best_hour
        
        return optimal
    
    def _test_strategy(self, trades: List, session: str, be_strategy: str, r_target: float, time_filter: str = 'all', optimal_hours: Dict = None) -> Dict:
        """Test a specific strategy configuration"""
        # Handle combined sessions
        if '+' in session:
            session_list = session.split('+')
            session_trades = [t for t in trades if t['session'] in session_list]
        else:
            session_trades = [t for t in trades if t['session'] == session]
        
        # Apply time filter
        if time_filter == 'optimal' and optimal_hours:
            filtered = []
            for t in session_trades:
                if not t.get('time'):
                    continue
                hour = int(t['time'].split(':')[0])
                if optimal_hours.get(t['session']) == hour:
                    filtered.append(t)
            session_trades = filtered
        elif time_filter == 'macro':
            session_trades = [t for t in session_trades if t.get('time') and 
                            (int(t['time'].split(':')[1]) >= 45 or int(t['time'].split(':')[1]) <= 15)]
        
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
        
        # Drawdown
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
        
        # Downside deviation (for Sortino)
        downside_returns = [r for r in results if r < 0]
        downside_dev = math.sqrt(sum(r**2 for r in downside_returns) / len(downside_returns)) if downside_returns else 0.01
        sortino = expectancy / downside_dev if downside_dev > 0 else 0
        
        # Omega ratio
        gains = sum(r for r in results if r > 0)
        losses = abs(sum(r for r in results if r < 0))
        omega = gains / losses if losses > 0 else 0
        
        return {
            'session': session,
            'be_strategy': be_strategy,
            'r_target': r_target,
            'time_filter': time_filter,
            'expectancy': expectancy,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_r': total_r,
            'total_trades': len(results),
            'max_drawdown': max_dd,
            'sortino_ratio': sortino,
            'omega_ratio': omega
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
