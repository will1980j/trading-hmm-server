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
    
    def update(self, bar: dict, debug=False) -> str:
        """
        Update bias for new bar (bar-close logic only)
        
        Args:
            bar: dict with keys: ts, open, high, low, close
            debug: if True, print detailed debug info
        
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
                if debug:
                    print(f"  [ATH break] close {close:.2f} > prev_ATH {self.prev_ath:.2f} -> Bullish")
                self.bias = "Bullish"
            elif close < self.prev_atl and self.bias != "Bearish":
                if debug:
                    print(f"  [ATL break] close {close:.2f} < prev_ATL {self.prev_atl:.2f} -> Bearish")
                self.bias = "Bearish"
        
        # FVG detection (requires 3 bars of history)
        if self.prev_prev_high is not None:
            c2_high = self.prev_prev_high
            c2_low = self.prev_prev_low
            c0_high = high
            c0_low = low
            
            # Bullish FVG: c2_high < c0_low
            if c2_high < c0_low:
                if debug:
                    print(f"  [Bull FVG created] c2_high {c2_high:.2f} < c0_low {c0_low:.2f}")
                self.bull_fvg_highs.append(c0_low)
                self.bull_fvg_lows.append(c2_high)
            
            # Bearish FVG: c2_low > c0_high
            if c2_low > c0_high:
                if debug:
                    print(f"  [Bear FVG created] c2_low {c2_low:.2f} > c0_high {c0_high:.2f}")
                self.bear_fvg_highs.append(c2_low)
                self.bear_fvg_lows.append(c0_high)
        
        # Check for IFVG (inverse FVG) - bullish FVG becomes bearish IFVG
        i = len(self.bull_fvg_highs) - 1
        while i >= 0:
            if close < self.bull_fvg_lows[i]:
                if debug:
                    print(f"  [Bull FVG -> Bear IFVG] close {close:.2f} < bull_fvg_low {self.bull_fvg_lows[i]:.2f} -> Bearish")
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
                if debug:
                    print(f"  [Bear FVG -> Bull IFVG] close {close:.2f} > bear_fvg_high {self.bear_fvg_highs[i]:.2f} -> Bullish")
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
                if debug:
                    print(f"  [Bear IFVG cleanup] close {close:.2f} > bear_ifvg_high {self.bear_ifvg_highs[i]:.2f} -> Bullish")
                del self.bear_ifvg_highs[i]
                del self.bear_ifvg_lows[i]
                self.bias = "Bullish"
            i -= 1
        
        # Clean up invalidated IFVGs - bullish IFVG
        i = len(self.bull_ifvg_highs) - 1
        while i >= 0:
            if close < self.bull_ifvg_lows[i]:
                if debug:
                    print(f"  [Bull IFVG cleanup] close {close:.2f} < bull_ifvg_low {self.bull_ifvg_lows[i]:.2f} -> Bearish")
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
