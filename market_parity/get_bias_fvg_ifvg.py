"""
Parity V1: FVG/IFVG Bias Engine
Exact translation of Pine Script get_bias() function
"""

class BiasEngineFvgIfvg:
    def __init__(self):
        self.bias = "Neutral"
        self.ath = None
        self.atl = None
        self.prev_ath = None
        self.prev_atl = None
        self.bull_fvg_highs = []
        self.bull_fvg_lows = []
        self.bear_fvg_highs = []
        self.bear_fvg_lows = []
        self.bull_ifvg_highs = []
        self.bull_ifvg_lows = []
        self.bear_ifvg_highs = []
        self.bear_ifvg_lows = []
        self.prev_high = None
        self.prev_low = None
        self.prev_prev_high = None
        self.prev_prev_low = None
    
    def update(self, bar: dict) -> str:
        """
        Update bias for new bar (bar-close logic only)
        
        Args:
            bar: dict with keys: ts, open, high, low, close
        
        Returns:
            bias: "Bullish", "Bearish", or "Neutral"
        """
        high = bar['high']
        low = bar['low']
        close = bar['close']
        
        # Store previous ATH/ATL before updating
        self.prev_ath = self.ath
        self.prev_atl = self.atl
        
        # Update ATH/ATL
        if self.ath is None:
            self.ath = high
        else:
            self.ath = max(self.ath, high)
        
        if self.atl is None:
            self.atl = low
        else:
            self.atl = min(self.atl, low)
        
        # Check bias change on ATH/ATL break (using PREVIOUS ATH/ATL)
        if self.prev_ath is not None:
            if close > self.prev_ath and self.bias != "Bullish":
                self.bias = "Bullish"
            elif close < self.prev_atl and self.bias != "Bearish":
                self.bias = "Bearish"
        
        # FVG detection (requires 3 bars of history)
        if self.prev_prev_high is not None:
            c2_high = self.prev_prev_high
            c2_low = self.prev_prev_low
            c0_high = high
            c0_low = low
            
            # Bullish FVG: c2_high < c0_low
            if c2_high < c0_low:
                self.bull_fvg_highs.append(c0_low)
                self.bull_fvg_lows.append(c2_high)
            
            # Bearish FVG: c2_low > c0_high
            if c2_low > c0_high:
                self.bear_fvg_highs.append(c2_low)
                self.bear_fvg_lows.append(c0_high)
        
        # Check for IFVG (inverse FVG) - bullish FVG becomes bearish IFVG
        i = len(self.bull_fvg_highs) - 1
        while i >= 0:
            if close < self.bull_fvg_lows[i]:
                self.bear_ifvg_highs.append(self.bull_fvg_highs[i])
                self.bear_ifvg_lows.append(self.bull_fvg_lows[i])
                del self.bull_fvg_highs[i]
                del self.bull_fvg_lows[i]
                self.bias = "Bearish"
            i -= 1
        
        # Check for IFVG - bearish FVG becomes bullish IFVG
        i = len(self.bear_fvg_highs) - 1
        while i >= 0:
            if close > self.bear_fvg_highs[i]:
                self.bull_ifvg_highs.append(self.bear_fvg_highs[i])
                self.bull_ifvg_lows.append(self.bear_fvg_lows[i])
                del self.bear_fvg_highs[i]
                del self.bear_fvg_lows[i]
                self.bias = "Bullish"
            i -= 1
        
        # Clean up invalidated IFVGs - bearish IFVG
        i = len(self.bear_ifvg_highs) - 1
        while i >= 0:
            if close > self.bear_ifvg_highs[i]:
                del self.bear_ifvg_highs[i]
                del self.bear_ifvg_lows[i]
                self.bias = "Bullish"
            i -= 1
        
        # Clean up invalidated IFVGs - bullish IFVG
        i = len(self.bull_ifvg_highs) - 1
        while i >= 0:
            if close < self.bull_ifvg_lows[i]:
                del self.bull_ifvg_highs[i]
                del self.bull_ifvg_lows[i]
                self.bias = "Bearish"
            i -= 1
        
        # Update history for next bar
        self.prev_prev_high = self.prev_high
        self.prev_prev_low = self.prev_low
        self.prev_high = high
        self.prev_low = low
        
        return self.bias
