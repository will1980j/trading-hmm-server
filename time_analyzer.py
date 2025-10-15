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
    
    return {
        'total_trades': len(trades),
        'overall_expectancy': overall_expectancy,
        'hourly': hourly,
        'session': session,
        'day_of_week': day_of_week,
        'week_of_month': week_of_month,
        'monthly': monthly,
        'best_hour': {'hour': f"{best_hour['hour']}:00", 'expectancy': best_hour['expectancy']},
        'best_session': {'session': best_session['session'], 'expectancy': best_session['expectancy']},
        'best_day': {'day': best_day['day'], 'expectancy': best_day['expectancy']},
        'best_month': {'month': best_month['month'], 'expectancy': best_month.get('expectancy', 0)}
    }

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

def generate_empty_analysis():
    """Return empty analysis structure"""
    return {
        'total_trades': 0,
        'overall_expectancy': 0,
        'hourly': [],
        'session': [],
        'day_of_week': [],
        'week_of_month': [],
        'monthly': [],
        'best_hour': {'hour': 'N/A', 'expectancy': 0},
        'best_session': {'session': 'N/A', 'expectancy': 0},
        'best_day': {'day': 'N/A', 'expectancy': 0},
        'best_month': {'month': 'N/A', 'expectancy': 0}
    }
