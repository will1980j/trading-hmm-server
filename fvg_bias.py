"""
FVG Bias Calculator based on the TradingView indicator
Replicates the Multi-Instrument FVG Scanner logic
"""

class FVGBiasCalculator:
    def __init__(self):
        self.bull_fvg_highs = []
        self.bull_fvg_lows = []
        self.bear_fvg_highs = []
        self.bear_fvg_lows = []
        self.bull_ifvg_highs = []
        self.bull_ifvg_lows = []
        self.bear_ifvg_highs = []
        self.bear_ifvg_lows = []
        self.bias = "Neutral"
    
    def calculate_bias(self, price_data):
        """
        Calculate FVG bias based on the indicator logic
        price_data should contain: high, low, close arrays
        """
        if not price_data or len(price_data.get('high', [])) < 3:
            return "Neutral"
        
        highs = price_data['high']
        lows = price_data['low']
        closes = price_data['close']
        
        # Get the last 3 candles (current logic uses [2], [1], [0])
        if len(highs) >= 3:
            c2_high = highs[-3]  # high[2] 
            c2_low = lows[-3]    # low[2]
            c0_high = highs[-1]  # high (current)
            c0_low = lows[-1]    # low (current)
            current_close = closes[-1]
            
            # FVG Detection Logic from indicator
            bullish_fvg = c2_high < c0_low  # Gap up
            bearish_fvg = c2_low > c0_high  # Gap down
            
            # Add new FVGs
            if bullish_fvg:
                self.bull_fvg_highs.append(c0_low)
                self.bull_fvg_lows.append(c2_high)
            
            if bearish_fvg:
                self.bear_fvg_highs.append(c2_low)
                self.bear_fvg_lows.append(c0_high)
            
            # Process existing FVGs for IFVG conversion
            # Bullish FVGs that get violated become Bearish IFVGs
            for i in range(len(self.bull_fvg_highs) - 1, -1, -1):
                if current_close < self.bull_fvg_lows[i]:
                    self.bear_ifvg_highs.append(self.bull_fvg_highs[i])
                    self.bear_ifvg_lows.append(self.bull_fvg_lows[i])
                    del self.bull_fvg_highs[i]
                    del self.bull_fvg_lows[i]
                    self.bias = "Bearish"
            
            # Bearish FVGs that get violated become Bullish IFVGs  
            for i in range(len(self.bear_fvg_highs) - 1, -1, -1):
                if current_close > self.bear_fvg_highs[i]:
                    self.bull_ifvg_highs.append(self.bear_fvg_highs[i])
                    self.bull_ifvg_lows.append(self.bear_fvg_lows[i])
                    del self.bear_fvg_highs[i]
                    del self.bear_fvg_lows[i]
                    self.bias = "Bullish"
            
            # Clean up IFVGs that get violated
            for i in range(len(self.bear_ifvg_highs) - 1, -1, -1):
                if current_close > self.bear_ifvg_highs[i]:
                    del self.bear_ifvg_highs[i]
                    del self.bear_ifvg_lows[i]
                    self.bias = "Bullish"
            
            for i in range(len(self.bull_ifvg_highs) - 1, -1, -1):
                if current_close < self.bull_ifvg_lows[i]:
                    del self.bull_ifvg_highs[i]
                    del self.bull_ifvg_lows[i]
                    self.bias = "Bearish"
        
        return self.bias
    
    def get_multi_timeframe_bias(self, price_data_dict):
        """
        Get bias for multiple timeframes like the indicator
        price_data_dict: {'1H': price_data, '15M': price_data, etc.}
        """
        biases = {}
        
        for timeframe, data in price_data_dict.items():
            # Create separate calculator for each timeframe
            tf_calculator = FVGBiasCalculator()
            biases[timeframe] = tf_calculator.calculate_bias(data)
        
        return biases
    
    def check_htf_alignment(self, biases, selected_timeframes):
        """
        Check if all selected timeframes align (like the indicator)
        """
        if not biases:
            return "NEUTRAL"
        
        # Check bullish alignment
        bullish_aligned = True
        bearish_aligned = True
        
        for tf in selected_timeframes:
            if tf in biases:
                if biases[tf] != "Bullish":
                    bullish_aligned = False
                if biases[tf] != "Bearish":
                    bearish_aligned = False
        
        if bullish_aligned:
            return "BULLISH"
        elif bearish_aligned:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def get_active_fvgs(self):
        """Get currently active FVGs and IFVGs"""
        return {
            'bull_fvgs': list(zip(self.bull_fvg_highs, self.bull_fvg_lows)),
            'bear_fvgs': list(zip(self.bear_fvg_highs, self.bear_fvg_lows)),
            'bull_ifvgs': list(zip(self.bull_ifvg_highs, self.bull_ifvg_lows)),
            'bear_ifvgs': list(zip(self.bear_ifvg_highs, self.bear_ifvg_lows))
        }