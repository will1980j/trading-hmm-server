"""
Time-based performance analysis for trading data
Analyzes R-value distributions across multiple time windows
"""
from datetime import datetime
import statistics

def analyze_time_performance(db):
    """Analyze trading performance across all time windows"""
    
    cursor = db.conn.cursor()
    
    # Get all trades with time and MFE data
    cursor.execute("""
        SELECT date, time, session, 
               COALESCE(mfe_none, mfe, 0) as r_value
        FROM signal_lab_trades 
        WHERE COALESCE(mfe_none, mfe, 0) != 0
        AND date IS NOT NULL
        AND time IS NOT NULL
        ORDER BY date, time
    """)
    
    trades = cursor.fetchall()
    
    if not trades:
        return generate_empty_analysis()
    
    # Analyze each time window
    macro = analyze_macro_windows(trades)
    hourly = analyze_hourly(trades)
    session = analyze_session(trades)
    day_of_week = analyze_day_of_week(trades)
    week_of_month = analyze_week_of_month(trades)
    monthly = analyze_monthly(trades)
    
    # Calculate overall stats
    all_r_values = [t['r_value'] for t in trades]
    overall_expectancy = statistics.mean(all_r_values)
    
    # Find best performers
    best_hour = max(hourly, key=lambda x: x['expectancy'])
    best_session = max(session, key=lambda x: x['expectancy'])
    best_day = max(day_of_week, key=lambda x: x['expectancy'])
    best_month = max(monthly, key=lambda x: x['expectancy']) if monthly else {'month': 'N/A'}
    
    # Analyze session hotspots
    session_hotspots = analyze_session_hotspots(hourly, session, trades)
    
    return {
        'total_trades': len(trades),
        'overall_expectancy': overall_expectancy,
        'macro': macro,
        'hourly': hourly,
        'session': session,
        'day_of_week': day_of_week,
        'week_of_month': week_of_month,
        'monthly': monthly,
        'best_hour': {'hour': f"{best_hour['hour']}:00", 'expectancy': best_hour['expectancy']},
        'best_session': {'session': best_session['session'], 'expectancy': best_session['expectancy']},
        'best_day': {'day': best_day['day'], 'expectancy': best_day['expectancy']},
        'best_month': {'month': best_month['month'], 'expectancy': best_month.get('expectancy', 0)},
        'session_hotspots': session_hotspots
    }

def analyze_macro_windows(trades):
    """Analyze macro windows (xx:50-xx:10 + MOC 15:15-15:45) vs non-macro"""
    macro_trades = []
    non_macro_trades = []
    
    for trade in trades:
        try:
            time_str = str(trade['time']) if trade['time'] else ''
            if not time_str or ':' not in time_str:
                continue
            hour = int(time_str.split(':')[0])
            minute = int(time_str.split(':')[1])
            
            is_macro = False
            # MOC window: 15:15-15:45
            if hour == 15 and 15 <= minute <= 45:
                is_macro = True
            # Hourly macros: xx:50-xx:10 (50-59 of current hour, 0-10 of next hour)
            elif minute >= 50 or minute <= 10:
                is_macro = True
            
            if is_macro:
                macro_trades.append(float(trade['r_value']))
            else:
                non_macro_trades.append(float(trade['r_value']))
        except:
            continue
    
    results = []
    if macro_trades:
        results.append({
            'window': 'Macro (xx:50-xx:10 + MOC)',
            'trades': len(macro_trades),
            'expectancy': statistics.mean(macro_trades),
            'win_rate': len([r for r in macro_trades if r > 0]) / len(macro_trades),
            'avg_r': statistics.mean(macro_trades),
            'std_dev': statistics.stdev(macro_trades) if len(macro_trades) > 1 else 0
        })
    
    if non_macro_trades:
        results.append({
            'window': 'Non-Macro',
            'trades': len(non_macro_trades),
            'expectancy': statistics.mean(non_macro_trades),
            'win_rate': len([r for r in non_macro_trades if r > 0]) / len(non_macro_trades),
            'avg_r': statistics.mean(non_macro_trades),
            'std_dev': statistics.stdev(non_macro_trades) if len(non_macro_trades) > 1 else 0
        })
    
    return results

def analyze_hourly(trades):
    """Analyze by hour of day (0-23)"""
    hourly_data = {}
    
    for trade in trades:
        try:
            time_str = str(trade['time']) if trade['time'] else ''
            if not time_str or ':' not in time_str:
                continue
            hour = int(time_str.split(':')[0])
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(float(trade['r_value']))
        except Exception as e:
            continue
    
    results = []
    for hour in range(24):
        if hour in hourly_data:
            r_values = hourly_data[hour]
            results.append({
                'hour': hour,
                'trades': len(r_values),
                'expectancy': statistics.mean(r_values),
                'win_rate': len([r for r in r_values if r > 0]) / len(r_values),
                'avg_r': statistics.mean(r_values),
                'std_dev': statistics.stdev(r_values) if len(r_values) > 1 else 0
            })
        else:
            results.append({
                'hour': hour,
                'trades': 0,
                'expectancy': 0,
                'win_rate': 0,
                'avg_r': 0,
                'std_dev': 0
            })
    
    return results

def analyze_session(trades):
    """Analyze by trading session"""
    session_data = {}
    
    for trade in trades:
        session = trade['session'] or 'Unknown'
        if session not in session_data:
            session_data[session] = []
        session_data[session].append(trade['r_value'])
    
    results = []
    for session, r_values in session_data.items():
        results.append({
            'session': session,
            'trades': len(r_values),
            'expectancy': statistics.mean(r_values),
            'win_rate': len([r for r in r_values if r > 0]) / len(r_values),
            'avg_r': statistics.mean(r_values),
            'std_dev': statistics.stdev(r_values) if len(r_values) > 1 else 0
        })
    
    return sorted(results, key=lambda x: x['expectancy'], reverse=True)

def analyze_day_of_week(trades):
    """Analyze by day of week"""
    day_data = {}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for trade in trades:
        try:
            date_obj = datetime.strptime(str(trade['date']), '%Y-%m-%d')
            day_name = day_names[date_obj.weekday()]
            if day_name not in day_data:
                day_data[day_name] = []
            day_data[day_name].append(trade['r_value'])
        except:
            continue
    
    results = []
    for day in day_names:
        if day in day_data:
            r_values = day_data[day]
            results.append({
                'day': day,
                'trades': len(r_values),
                'expectancy': statistics.mean(r_values),
                'win_rate': len([r for r in r_values if r > 0]) / len(r_values),
                'avg_r': statistics.mean(r_values),
                'std_dev': statistics.stdev(r_values) if len(r_values) > 1 else 0
            })
    
    return results

def analyze_week_of_month(trades):
    """Analyze by week of month (1-5)"""
    week_data = {}
    
    for trade in trades:
        try:
            date_obj = datetime.strptime(str(trade['date']), '%Y-%m-%d')
            week = (date_obj.day - 1) // 7 + 1
            if week not in week_data:
                week_data[week] = []
            week_data[week].append(trade['r_value'])
        except:
            continue
    
    results = []
    for week in sorted(week_data.keys()):
        r_values = week_data[week]
        results.append({
            'week': week,
            'trades': len(r_values),
            'expectancy': statistics.mean(r_values),
            'win_rate': len([r for r in r_values if r > 0]) / len(r_values),
            'avg_r': statistics.mean(r_values),
            'std_dev': statistics.stdev(r_values) if len(r_values) > 1 else 0
        })
    
    return results

def analyze_monthly(trades):
    """Analyze by month"""
    month_data = {}
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for trade in trades:
        try:
            date_obj = datetime.strptime(str(trade['date']), '%Y-%m-%d')
            month = month_names[date_obj.month - 1]
            if month not in month_data:
                month_data[month] = []
            month_data[month].append(trade['r_value'])
        except:
            continue
    
    results = []
    for month in month_names:
        if month in month_data:
            r_values = month_data[month]
            results.append({
                'month': month,
                'trades': len(r_values),
                'expectancy': statistics.mean(r_values),
                'win_rate': len([r for r in r_values if r > 0]) / len(r_values),
                'avg_r': statistics.mean(r_values),
                'std_dev': statistics.stdev(r_values) if len(r_values) > 1 else 0
            })
    
    return results

def analyze_session_hotspots(hourly_data, session_data, trades):
    """
    Analyze per-session R hotspots using hourly + session breakdown.
    
    Args:
        hourly_data: list with hour-level R and trades (0-23)
        session_data: list with session-level performance
        trades: raw trade data with time, session, r_value
    
    Returns:
        {
            "sessions": {
                "NY AM": {
                    "hot_hours": ["09:00", "10:00"],
                    "cold_hours": ["11:00"],
                    "avg_r": float,
                    "win_rate": float,
                    "density": float,  # trades per hour
                    "total_trades": int
                },
                ...
            }
        }
    """
    # Session hour mappings (US Eastern Time)
    session_hour_map = {
        'ASIA': list(range(20, 24)),  # 20:00-23:59
        'LONDON': list(range(0, 6)),  # 00:00-05:59
        'NY PRE': list(range(6, 9)),  # 06:00-08:59 (includes 08:00-08:29)
        'NY AM': list(range(9, 12)),  # 09:00-11:59 (market open 08:30, but 09:00-11:59 for full hours)
        'NY LUNCH': [12],  # 12:00-12:59
        'NY PM': list(range(13, 16))  # 13:00-15:59
    }
    
    # Build session-hour performance map
    session_hour_performance = {}
    
    for trade in trades:
        try:
            time_str = str(trade['time']) if trade['time'] else ''
            if not time_str or ':' not in time_str:
                continue
            
            hour = int(time_str.split(':')[0])
            session = trade['session'] or 'Unknown'
            r_value = float(trade['r_value'])
            
            if session not in session_hour_performance:
                session_hour_performance[session] = {}
            
            if hour not in session_hour_performance[session]:
                session_hour_performance[session][hour] = []
            
            session_hour_performance[session][hour].append(r_value)
        except:
            continue
    
    # Build hotspots for each session
    sessions_result = {}
    
    for session_name, hour_list in session_hour_map.items():
        if session_name not in session_hour_performance:
            continue
        
        session_hours = session_hour_performance[session_name]
        
        # Calculate per-hour stats within this session
        hour_stats = []
        for hour in hour_list:
            if hour in session_hours and len(session_hours[hour]) >= 3:  # Min 3 trades for significance
                r_values = session_hours[hour]
                hour_stats.append({
                    'hour': hour,
                    'avg_r': statistics.mean(r_values),
                    'trades': len(r_values),
                    'win_rate': len([r for r in r_values if r > 0]) / len(r_values)
                })
        
        if not hour_stats:
            continue
        
        # Sort by avg_r to find hot/cold hours
        hour_stats.sort(key=lambda x: x['avg_r'], reverse=True)
        
        # Top 1-2 hours are "hot" (positive R preferred)
        hot_hours = [f"{h['hour']:02d}:00" for h in hour_stats[:2] if h['avg_r'] > 0]
        
        # Bottom hour is "cold" if negative or significantly lower
        cold_hours = []
        if len(hour_stats) > 2 and hour_stats[-1]['avg_r'] < 0:
            cold_hours = [f"{hour_stats[-1]['hour']:02d}:00"]
        
        # Calculate session-level aggregates
        all_session_trades = []
        for hour in hour_list:
            if hour in session_hours:
                all_session_trades.extend(session_hours[hour])
        
        if all_session_trades:
            total_trades = len(all_session_trades)
            avg_r = statistics.mean(all_session_trades)
            win_rate = len([r for r in all_session_trades if r > 0]) / total_trades
            density = total_trades / len(hour_list)  # trades per hour
            
            sessions_result[session_name] = {
                'hot_hours': hot_hours,
                'cold_hours': cold_hours,
                'avg_r': round(avg_r, 3),
                'win_rate': round(win_rate, 3),
                'density': round(density, 2),
                'total_trades': total_trades
            }
    
    return {'sessions': sessions_result}

def generate_empty_analysis():
    """Return empty analysis structure"""
    return {
        'total_trades': 0,
        'overall_expectancy': 0,
        'macro': [],
        'hourly': [],
        'session': [],
        'day_of_week': [],
        'week_of_month': [],
        'monthly': [],
        'best_hour': {'hour': 'N/A', 'expectancy': 0},
        'best_session': {'session': 'N/A', 'expectancy': 0},
        'session_hotspots': {'sessions': {}},
        'best_day': {'day': 'N/A', 'expectancy': 0},
        'best_month': {'month': 'N/A', 'expectancy': 0}
    }
