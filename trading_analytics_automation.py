import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json

class TradingAnalytics:
    def __init__(self, credentials_path=None):
        self.credentials_path = credentials_path
        self.gc = None
        if credentials_path:
            self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection"""
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
        self.gc = gspread.authorize(creds)
    
    def calculate_trade_metrics(self, trades_df):
        """Calculate comprehensive trading metrics"""
        metrics = {}
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['PnL'] > 0])
        losing_trades = len(trades_df[trades_df['PnL'] < 0])
        
        metrics['total_trades'] = total_trades
        metrics['winning_trades'] = winning_trades
        metrics['losing_trades'] = losing_trades
        metrics['win_rate'] = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # PnL metrics
        total_pnl = trades_df['PnL'].sum()
        avg_win = trades_df[trades_df['PnL'] > 0]['PnL'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['PnL'] < 0]['PnL'].mean() if losing_trades > 0 else 0
        
        metrics['total_pnl'] = total_pnl
        metrics['avg_win'] = avg_win
        metrics['avg_loss'] = abs(avg_loss)
        metrics['profit_factor'] = (avg_win * winning_trades) / (abs(avg_loss) * losing_trades) if losing_trades > 0 else float('inf')
        
        # Risk metrics
        metrics['max_drawdown'] = self.calculate_max_drawdown(trades_df)
        metrics['sharpe_ratio'] = self.calculate_sharpe_ratio(trades_df)
        metrics['expectancy'] = (metrics['win_rate']/100 * avg_win) + ((100-metrics['win_rate'])/100 * avg_loss)
        
        # Streak analysis
        streaks = self.calculate_streaks(trades_df)
        metrics.update(streaks)
        
        return metrics
    
    def calculate_max_drawdown(self, trades_df):
        """Calculate maximum drawdown"""
        cumulative_pnl = trades_df['PnL'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = cumulative_pnl - running_max
        return drawdown.min()
    
    def calculate_sharpe_ratio(self, trades_df, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        returns = trades_df['PnL']
        excess_returns = returns.mean() - risk_free_rate/252
        return excess_returns / returns.std() if returns.std() != 0 else 0
    
    def calculate_streaks(self, trades_df):
        """Calculate winning and losing streaks"""
        trades_df['win'] = trades_df['PnL'] > 0
        trades_df['streak_id'] = (trades_df['win'] != trades_df['win'].shift()).cumsum()
        
        streaks = trades_df.groupby('streak_id').agg({
            'win': 'first',
            'PnL': 'count'
        }).rename(columns={'PnL': 'streak_length'})
        
        win_streaks = streaks[streaks['win']]['streak_length']
        loss_streaks = streaks[~streaks['win']]['streak_length']
        
        return {
            'max_win_streak': win_streaks.max() if len(win_streaks) > 0 else 0,
            'max_loss_streak': loss_streaks.max() if len(loss_streaks) > 0 else 0,
            'avg_win_streak': win_streaks.mean() if len(win_streaks) > 0 else 0,
            'avg_loss_streak': loss_streaks.mean() if len(loss_streaks) > 0 else 0
        }
    
    def analyze_by_timeframe(self, trades_df):
        """Analyze performance by different timeframes"""
        trades_df['hour'] = pd.to_datetime(trades_df['Date']).dt.hour
        trades_df['day_of_week'] = pd.to_datetime(trades_df['Date']).dt.dayofweek
        trades_df['month'] = pd.to_datetime(trades_df['Date']).dt.month
        
        analysis = {}
        
        # Hourly analysis
        hourly = trades_df.groupby('hour').agg({
            'PnL': ['count', 'sum', 'mean'],
            'Direction': lambda x: (x == 'LONG').sum() / len(x) * 100
        }).round(2)
        analysis['hourly'] = hourly
        
        # Daily analysis
        daily = trades_df.groupby('day_of_week').agg({
            'PnL': ['count', 'sum', 'mean']
        }).round(2)
        analysis['daily'] = daily
        
        # Monthly analysis
        monthly = trades_df.groupby('month').agg({
            'PnL': ['count', 'sum', 'mean']
        }).round(2)
        analysis['monthly'] = monthly
        
        return analysis
    
    def analyze_by_symbol(self, trades_df):
        """Analyze performance by trading symbol"""
        symbol_analysis = trades_df.groupby('Symbol').agg({
            'PnL': ['count', 'sum', 'mean'],
            'Direction': lambda x: (x == 'LONG').sum() / len(x) * 100 if len(x) > 0 else 0
        }).round(2)
        
        # Calculate win rate by symbol
        win_rates = trades_df.groupby('Symbol').apply(
            lambda x: (x['PnL'] > 0).sum() / len(x) * 100
        ).round(2)
        
        symbol_analysis[('Win_Rate', '')] = win_rates
        
        return symbol_analysis
    
    def update_google_sheet(self, sheet_name, metrics, timeframe_analysis, symbol_analysis):
        """Update Google Sheet with calculated metrics"""
        if not self.gc:
            print("Google Sheets not configured")
            return
        
        try:
            sheet = self.gc.open(sheet_name)
            
            # Update metrics sheet
            metrics_ws = sheet.worksheet('Metrics')
            metrics_data = [[k, v] for k, v in metrics.items()]
            metrics_ws.update('A1', [['Metric', 'Value']] + metrics_data)
            
            # Update timeframe analysis
            hourly_ws = sheet.worksheet('Hourly_Analysis')
            hourly_data = timeframe_analysis['hourly'].reset_index().values.tolist()
            hourly_ws.update('A1', [['Hour'] + list(timeframe_analysis['hourly'].columns)] + hourly_data)
            
            # Update symbol analysis
            symbol_ws = sheet.worksheet('Symbol_Analysis')
            symbol_data = symbol_analysis.reset_index().values.tolist()
            symbol_ws.update('A1', [['Symbol'] + list(symbol_analysis.columns)] + symbol_data)
            
            print(f"Successfully updated {sheet_name}")
            
        except Exception as e:
            print(f"Error updating sheet: {e}")

def main():
    # Example usage
    analytics = TradingAnalytics()
    
    # Sample data structure based on your image
    sample_data = {
        'Date': ['1-Jul', '1-Jul', '1-Jul', '1-Jul', '1-Jul'],
        'Month': ['July', 'July', 'July', 'July', 'July'],
        'Week': [27, 27, 27, 27, 27],
        'Day': ['Tuesday', 'Tuesday', 'Tuesday', 'Tuesday', 'Tuesday'],
        'Direction': ['LONG', 'LONG', 'LONG', 'LONG', 'LONG'],
        'Symbol': ['LONDON', 'LONDON', 'LONDON', 'LONDON', 'NY PRE MARKET'],
        'PnL': [1.0, -1.0, 0.0, -1.0, 0.0]  # Example PnL values
    }
    
    trades_df = pd.DataFrame(sample_data)
    
    # Calculate metrics
    metrics = analytics.calculate_trade_metrics(trades_df)
    timeframe_analysis = analytics.analyze_by_timeframe(trades_df)
    symbol_analysis = analytics.analyze_by_symbol(trades_df)
    
    print("Trading Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    return analytics, metrics, timeframe_analysis, symbol_analysis

if __name__ == "__main__":
    main()