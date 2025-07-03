//@version=6
indicator("Multi-TF Market State Tracker", overlay=true)

// Base theme colors and constants
var color BG_COLOR = color.rgb(28, 28, 53, 90)  // Almost invisible background
var color HEADER_BG = color.rgb(35, 35, 65, 80)  // Subtle header
var color TEXT_COLOR = color.rgb(255, 255, 255)  // Bright white text
var color HEADER_TEXT = color.rgb(255, 255, 255)
var color bullishBgColor = color.rgb(0, 255, 0, 70)  // More transparent green
var color bearishBgColor = color.rgb(255, 0, 0, 70)  // More transparent red
var int tableBgTransparency = 90  // Very transparent
var int headerBgTransparency = 80  // Very transparent headers
var int cellBgTransparency = 85  // Very transparent cells

// Table style inputs
tableTextSize = input.string("Normal", "Table Text Size", options=["Tiny", "Small", "Normal", "Large", "Huge"], group="Table Style")
var float tableSize = input.float(1.0, "Table Size Multiplier", minval=0.5, maxval=2.0, step=0.1, group="Table Style")
var float tablePadding = input.float(1.0, "Cell Padding", minval=0.5, maxval=2.0, step=0.1, group="Table Style")

// Constants
var TF_MONTHLY = "M"
var TF_WEEKLY = "W"
var TF_DAILY = "D"
var TF_4H = "240"
var TF_1H = "60"
var TF_15 = "15"
var TF_5 = "5"
// State definitions
var STATE_BULL_ERL_TO_IRL = "BULLISH ERL ▼ IRL"
var STATE_BULL_IRL_TO_ERL = "BULLISH IRL ▲ ERL"
var STATE_BEAR_ERL_TO_IRL = "BEARISH ERL ▲ IRL"
var STATE_BEAR_IRL_TO_ERL = "BEARISH IRL ▼ ERL"

// State inputs
stateMonthly = input.string(title="Monthly State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
stateWeekly = input.string(title="Weekly State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
stateDaily = input.string(title="Daily State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
state4H = input.string(title="4H State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
state1H = input.string(title="1H State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
state15M = input.string(title="15M State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])
state5M = input.string(title="5M State", defval=STATE_BULL_ERL_TO_IRL, options=[STATE_BULL_ERL_TO_IRL, STATE_BULL_IRL_TO_ERL, STATE_BEAR_ERL_TO_IRL, STATE_BEAR_IRL_TO_ERL])

// Signal filter inputs
showStrongBullish = input.bool(true, "Show Strong Bullish Signals", inline="strong_signals", group="Signal Filters")
showStrongBearish = input.bool(true, "Show Strong Bearish Signals", inline="strong_signals", group="Signal Filters")
showStrongCounter = input.bool(true, "Show Strong Counter Signals", inline="strong_signals", group="Signal Filters")
showWeakBullish = input.bool(true, "Show Weak Bullish Signals", group="Signal Filters")
showWeakBearish = input.bool(true, "Show Weak Bearish Signals", group="Signal Filters")
showWeakAligned = input.bool(true, "Show Weak Aligned Signals", group="Signal Filters")
// FVG Settings
showMonthlyFVG = input.bool(false, "Show Monthly FVGs", group="FVG Settings")
showWeeklyFVG = input.bool(false, "Show Weekly FVGs", group="FVG Settings")
showDailyFVG = input.bool(false, "Show Daily FVGs", group="FVG Settings")
show4HFVG = input.bool(false, "Show 4H FVGs", group="FVG Settings")
show1HFVG = input.bool(false, "Show 1H FVGs", group="FVG Settings")
show15MFVG = input.bool(false, "Show 15M FVGs", group="FVG Settings")
show5MFVG = input.bool(true, "Show 5M FVGs", group="FVG Settings")
showChartTFFVG = input.bool(true, "Show Chart TF FVGs", group="FVG Settings")

// IFVG Settings
showMonthlyIFVG = input.bool(false, "Show Monthly IFVGs", group="IFVG Settings")
showWeeklyIFVG = input.bool(false, "Show Weekly IFVGs", group="IFVG Settings")
showDailyIFVG = input.bool(false, "Show Daily IFVGs", group="IFVG Settings")
show4HIFVG = input.bool(false, "Show 4H IFVGs", group="IFVG Settings")
show1HIFVG = input.bool(false, "Show 1H IFVGs", group="IFVG Settings")
show15MIFVG = input.bool(false, "Show 15M IFVGs", group="IFVG Settings")
show5MIFVG = input.bool(true, "Show 5M IFVGs", group="IFVG Settings")
showChartTFIFVG = input.bool(true, "Show Chart TF IFVGs", group="IFVG Settings")

// FVG Appearance
fvgHistoryLimit = input.int(10, "FVG History Limit", minval=1, maxval=100, group="FVG Appearance")
bullFVGColor = input.color(color.new(color.green, 90), "Bullish FVG Color", group="FVG Appearance")
bearFVGColor = input.color(color.new(color.red, 90), "Bearish FVG Color", group="FVG Appearance")
fvgBorderColor = input.color(color.new(color.white, 80), "FVG Border Color", group="FVG Appearance")
showFVGBorder = input.bool(true, "Show FVG Borders", group="FVG Appearance")
fvgExtension = input.int(50, "FVG Extension Bars", minval=10, maxval=500, group="FVG Appearance")
showCEMidpoint = input.bool(false, "Show CE Midpoints", group="FVG Appearance")
ceMidpointColor = input.color(color.new(color.yellow, 0), "CE Midpoint Color", group="FVG Appearance")
ceMidpointStyle = input.string("Dashed", "CE Midpoint Style", options=["Solid", "Dotted", "Dashed"], group="FVG Appearance")
fvgLabelSize = input.string("Tiny", "FVG Label Size", options=["Tiny", "Small", "Normal"], group="FVG Appearance")
fvgMaxPerTF = input.int(3, "Max FVGs Per Timeframe", minval=1, maxval=10, group="FVG Appearance")

// IFVG Appearance
bullIFVGColor = input.color(color.new(color.blue, 90), "Bullish IFVG Color", group="IFVG Appearance")
bearIFVGColor = input.color(color.new(color.purple, 90), "Bearish IFVG Color", group="IFVG Appearance")
ifvgBorderColor = input.color(color.new(color.white, 80), "IFVG Border Color", group="IFVG Appearance")
showIFVGBorder = input.bool(true, "Show IFVG Borders", group="IFVG Appearance")
ifvgMaxPerTF = input.int(3, "Max IFVGs Per Timeframe", minval=1, maxval=10, group="IFVG Appearance")

// Color inputs
bullErlIrlColor = input.color(title="BULLISH ERL to IRL Color", defval=color.rgb(120, 123, 198), group="State Colors")
bullIrlErlColor = input.color(title="BULLISH IRL to ERL Color", defval=color.rgb(101, 255, 255), group="State Colors")
bearErlIrlColor = input.color(title="BEARISH ERL to IRL Color", defval=color.rgb(198, 123, 120), group="State Colors")
bearIrlErlColor = input.color(title="BEARISH IRL to ERL Color", defval=color.rgb(255, 101, 101), group="State Colors")
textColor = input.color(title="Table Text Color", defval=TEXT_COLOR, group="Table Style")
headerTextColor = input.color(title="Header Text Color", defval=HEADER_TEXT, group="Table Style")

// Table creation with dynamic text size
var table stateTable = table.new(position.top_right, columns=3, rows=25, bgcolor=BG_COLOR, frame_width=1, frame_color=color.new(color.gray, 80), border_width=0, border_color=color.new(color.gray, 85))

// Helper functions
getTableTextSize(string size) =>
    switch size
        "Tiny" => size.tiny
        "Small" => size.small
        "Normal" => size.normal
        "Large" => size.large
        "Huge" => size.huge
        => size.normal

getTrendText(state) =>
    var string result = ""
    if state == STATE_BULL_ERL_TO_IRL
        result := "▼ Bullish Retracement"
    else if state == STATE_BULL_IRL_TO_ERL
        result := "▲ Bullish Expansion"
    else if state == STATE_BEAR_ERL_TO_IRL
        result := "▲ Bearish Retracement"
    else if state == STATE_BEAR_IRL_TO_ERL
        result := "▼ Bearish Expansion"
    result

getStateColor(state) =>
    state == STATE_BULL_ERL_TO_IRL ? color.new(bullErlIrlColor, cellBgTransparency + 10) : 
     state == STATE_BULL_IRL_TO_ERL ? color.new(bullIrlErlColor, cellBgTransparency + 10) : 
     state == STATE_BEAR_ERL_TO_IRL ? color.new(bearErlIrlColor, cellBgTransparency + 10) : 
     color.new(bearIrlErlColor, cellBgTransparency + 10)

getOpportunityStrength(string higherTFState, string lowerTFState) =>
    string result = ""
    if (higherTFState == STATE_BULL_IRL_TO_ERL and lowerTFState == STATE_BULL_IRL_TO_ERL) and showStrongBullish
        result := "STRONG BULLISH ▲"
    else if (higherTFState == STATE_BEAR_IRL_TO_ERL and lowerTFState == STATE_BEAR_IRL_TO_ERL) and showStrongBearish
        result := "STRONG BEARISH ▼"
    else if ((higherTFState == STATE_BULL_ERL_TO_IRL and lowerTFState == STATE_BULL_ERL_TO_IRL) or
             (higherTFState == STATE_BEAR_ERL_TO_IRL and lowerTFState == STATE_BEAR_ERL_TO_IRL)) and showStrongCounter
        result := "STRONG COUNTER " + (higherTFState == STATE_BULL_ERL_TO_IRL ? "▼" : "▲")
    else if (higherTFState == STATE_BULL_ERL_TO_IRL and lowerTFState == STATE_BULL_IRL_TO_ERL) and showWeakBullish
        result := "WEAK BULLISH ▲"
    else if (higherTFState == STATE_BEAR_ERL_TO_IRL and lowerTFState == STATE_BEAR_IRL_TO_ERL) and showWeakBearish
        result := "WEAK BEARISH ▼"
    else if showWeakAligned and ((str.contains(higherTFState, "BEARISH") and str.contains(lowerTFState, "BULLISH")) or
         (str.contains(higherTFState, "BULLISH") and str.contains(lowerTFState, "BEARISH"))) and
         ((higherTFState == STATE_BEAR_ERL_TO_IRL and lowerTFState == STATE_BULL_IRL_TO_ERL) or
          (higherTFState == STATE_BULL_IRL_TO_ERL and lowerTFState == STATE_BEAR_ERL_TO_IRL) or
          (higherTFState == STATE_BULL_ERL_TO_IRL and lowerTFState == STATE_BEAR_IRL_TO_ERL) or
          (higherTFState == STATE_BEAR_IRL_TO_ERL and lowerTFState == STATE_BULL_ERL_TO_IRL))
        result := "WEAK ALIGNED " + (higherTFState == STATE_BEAR_ERL_TO_IRL or higherTFState == STATE_BULL_IRL_TO_ERL ? "▲" : "▼")
    result

getOpportunityColor(string signal) =>
    color result = na
    if str.contains(signal, "STRONG BULLISH")
        result := color.new(bullishBgColor, cellBgTransparency + 5)
    else if str.contains(signal, "STRONG BEARISH")
        result := color.new(bearishBgColor, cellBgTransparency + 5)
    else if str.contains(signal, "STRONG COUNTER")
        result := color.new(color.yellow, cellBgTransparency + 10)
    else if str.contains(signal, "WEAK BULLISH")
        result := color.new(color.new(bullishBgColor, 80), cellBgTransparency + 5)
    else if str.contains(signal, "WEAK BEARISH")
        result := color.new(color.new(bearishBgColor, 80), cellBgTransparency + 5)
    else if str.contains(signal, "WEAK ALIGNED")
        result := color.new(color.blue, cellBgTransparency + 10)
    else
        result := color.new(color.gray, cellBgTransparency + 10)
    result

getEntryPoint(string timeframePair, string direction) =>
    var string result = ""
    if timeframePair == "Monthly-Weekly"
        result := direction == "▲" ? "Weekly Bullish PD Array" : direction == "▼" ? "Weekly Bearish PD Array" : ""
    else if timeframePair == "Weekly-Daily"
        result := direction == "▲" ? "Daily Bullish PD Array" : direction == "▼" ? "Daily Bearish PD Array" : ""
    else if timeframePair == "Daily-4H"
        result := direction == "▲" ? "4H Bullish PD Array" : direction == "▼" ? "4H Bearish PD Array" : ""
    else if timeframePair == "4H-1H"
        result := direction == "▲" ? "1H Bullish PD Array" : direction == "▼" ? "1H Bearish PD Array" : ""
    else if timeframePair == "1H-15M"
        result := direction == "▲" ? "15M Bullish PD Array" : direction == "▼" ? "15M Bearish PD Array" : ""
    else if timeframePair == "15M-5M"
        result := direction == "▲" ? "5M Bullish PD Array" : direction == "▼" ? "5M Bearish PD Array" : ""
    result

getFVGs(timeframe, bullIFVGArray, bearIFVGArray, terminatedFVGArray) =>
    var bullFVGs = array.new_box(0)
    var bearFVGs = array.new_box(0)
    var bullIFVGs = array.new_box(0)
    var bearIFVGs = array.new_box(0)
   
    // Get candle data including middle candle
    [h0, l0, h1, l1, h2, l2] = request.security(syminfo.tickerid, timeframe, [high, low, high[1], low[1], high[2], low[2]], lookahead=barmerge.lookahead_off)
    [o0, c0] = request.security(syminfo.tickerid, timeframe, [open, close], lookahead=barmerge.lookahead_off)
   
    // Regular FVG Detection
    // Bullish FVG: low[0] > high[2]
    if l0 > h2 and array.size(bullFVGs) < fvgMaxPerTF and ((timeframe == "M" and showMonthlyFVG) or (timeframe == "W" and showWeeklyFVG) or (timeframe == "D" and showDailyFVG) or (timeframe == "240" and show4HFVG) or (timeframe == "60" and show1HFVG) or (timeframe == "15" and show15MFVG) or (timeframe == "5" and show5MFVG) or (timeframe == timeframe.period and showChartTFFVG))
        borderCol = showFVGBorder ? fvgBorderColor : na
        textSize = fvgLabelSize == "Tiny" ? size.tiny : fvgLabelSize == "Small" ? size.small : size.normal
        newFVG = box.new(bar_index, l0, bar_index + fvgExtension, h2,
                         bgcolor=bullFVGColor,
                         border_color=borderCol,
                         border_width=1,
                         text="FVG " + timeframe,
                         text_color=color.white,
                         text_size=textSize,
                         text_halign=text.align_right,
                         extend=extend.right)
        array.push(bullFVGs, newFVG)

    // Bearish FVG: high[0] < low[2]
    if h0 < l2 and array.size(bearFVGs) < fvgMaxPerTF and ((timeframe == "M" and showMonthlyFVG) or (timeframe == "W" and showWeeklyFVG) or (timeframe == "D" and showDailyFVG) or (timeframe == "240" and show4HFVG) or (timeframe == "60" and show1HFVG) or (timeframe == "15" and show15MFVG) or (timeframe == "5" and show5MFVG) or (timeframe == timeframe.period and showChartTFFVG))
        borderCol = showFVGBorder ? fvgBorderColor : na
        textSize = fvgLabelSize == "Tiny" ? size.tiny : fvgLabelSize == "Small" ? size.small : size.normal
        newFVG = box.new(bar_index, l2, bar_index + fvgExtension, h0,
                         bgcolor=bearFVGColor,
                         border_color=borderCol,
                         border_width=1,
                         text="FVG " + timeframe,
                         text_color=color.white,
                         text_size=textSize,
                         text_halign=text.align_right,
                         extend=extend.right)
        array.push(bearFVGs, newFVG)

    // IFVG Detection
    // Bullish IFVG: low[1] > high[0] AND low[1] > high[2]
    if l1 > h0 and l1 > h2 and array.size(bullIFVGs) < ifvgMaxPerTF and ((timeframe == "M" and showMonthlyIFVG) or (timeframe == "W" and showWeeklyIFVG) or (timeframe == "D" and showDailyIFVG) or (timeframe == "240" and show4HIFVG) or (timeframe == "60" and show1HIFVG) or (timeframe == "15" and show15MIFVG) or (timeframe == "5" and show5MIFVG) or (timeframe == timeframe.period and showChartTFIFVG))
        borderCol = showIFVGBorder ? ifvgBorderColor : na
        textSize = fvgLabelSize == "Tiny" ? size.tiny : fvgLabelSize == "Small" ? size.small : size.normal
        newIFVG = box.new(bar_index, h0, bar_index + fvgExtension, l1,
                         bgcolor=bullIFVGColor,
                         border_color=borderCol,
                         border_width=1,
                         text="IFVG " + timeframe,
                         text_color=color.white,
                         text_size=textSize,
                         text_halign=text.align_right,
                         extend=extend.right)
        array.push(bullIFVGs, newIFVG)

    // Bearish IFVG: high[1] < low[0] AND high[1] < low[2]
    if h1 < l0 and h1 < l2 and array.size(bearIFVGs) < ifvgMaxPerTF and ((timeframe == "M" and showMonthlyIFVG) or (timeframe == "W" and showWeeklyIFVG) or (timeframe == "D" and showDailyIFVG) or (timeframe == "240" and show4HIFVG) or (timeframe == "60" and show1HIFVG) or (timeframe == "15" and show15MIFVG) or (timeframe == "5" and show5MIFVG) or (timeframe == timeframe.period and showChartTFIFVG))
        borderCol = showIFVGBorder ? ifvgBorderColor : na
        textSize = fvgLabelSize == "Tiny" ? size.tiny : fvgLabelSize == "Small" ? size.small : size.normal
        newIFVG = box.new(bar_index, l0, bar_index + fvgExtension, h1,
                         bgcolor=bearIFVGColor,
                         border_color=borderCol,
                         border_width=1,
                         text="IFVG " + timeframe,
                         text_color=color.white,
                         text_size=textSize,
                         text_halign=text.align_right,
                         extend=extend.right)
        array.push(bearIFVGs, newIFVG)

    [bullFVGs, bearFVGs, bullIFVGs, bearIFVGs]


// Create separate FVG arrays for each timeframe
var monthlyBullFVGs = array.new_box(0)
var monthlyBearFVGs = array.new_box(0)
var weeklyBullFVGs = array.new_box(0)
var weeklyBearFVGs = array.new_box(0)
var dailyBullFVGs = array.new_box(0)
var dailyBearFVGs = array.new_box(0)
var h4BullFVGs = array.new_box(0)
var h4BearFVGs = array.new_box(0)
var h1BullFVGs = array.new_box(0)
var h1BearFVGs = array.new_box(0)
var m15BullFVGs = array.new_box(0)
var m15BearFVGs = array.new_box(0)
var m5BullFVGs = array.new_box(0)
var m5BearFVGs = array.new_box(0)
var chartTFBullFVGs = array.new_box(0)
var chartTFBearFVGs = array.new_box(0)

// Create separate IFVG arrays for each timeframe
var monthlyBullIFVGs = array.new_box(0)
var monthlyBearIFVGs = array.new_box(0)
var weeklyBullIFVGs = array.new_box(0)
var weeklyBearIFVGs = array.new_box(0)
var dailyBullIFVGs = array.new_box(0)
var dailyBearIFVGs = array.new_box(0)
var h4BullIFVGs = array.new_box(0)
var h4BearIFVGs = array.new_box(0)
var h1BullIFVGs = array.new_box(0)
var h1BearIFVGs = array.new_box(0)
var m15BullIFVGs = array.new_box(0)
var m15BearIFVGs = array.new_box(0)
var m5BullIFVGs = array.new_box(0)
var m5BearIFVGs = array.new_box(0)
var chartTFBullIFVGs = array.new_box(0)
var chartTFBearIFVGs = array.new_box(0)

// Arrays to track terminated FVGs that might become IFVGs
var monthlyTerminatedFVGs = array.new_float(0)
var weeklyTerminatedFVGs = array.new_float(0)
var dailyTerminatedFVGs = array.new_float(0)
var h4TerminatedFVGs = array.new_float(0)
var h1TerminatedFVGs = array.new_float(0)
var m15TerminatedFVGs = array.new_float(0)
var m5TerminatedFVGs = array.new_float(0)
var chartTFTerminatedFVGs = array.new_float(0)

// Track last processed bar for each timeframe to prevent duplicate FVGs
var int lastMonthlyBar = 0
var int lastWeeklyBar = 0
var int lastDailyBar = 0
var int lastH4Bar = 0
var int lastH1Bar = 0
var int last15MBar = 0
var int last5MBar = 0

// Clear all FVG and IFVG boxes on first bar of chart
if barstate.isfirst
    array.clear(monthlyBullFVGs)
    array.clear(monthlyBearFVGs)
    array.clear(weeklyBullFVGs)
    array.clear(weeklyBearFVGs)
    array.clear(dailyBullFVGs)
    array.clear(dailyBearFVGs)
    array.clear(h4BullFVGs)
    array.clear(h4BearFVGs)
    array.clear(h1BullFVGs)
    array.clear(h1BearFVGs)
    array.clear(m15BullFVGs)
    array.clear(m15BearFVGs)
    array.clear(m5BullFVGs)
    array.clear(m5BearFVGs)
    array.clear(chartTFBullFVGs)
    array.clear(chartTFBearFVGs)

    // Clear IFVG arrays
    array.clear(monthlyBullIFVGs)
    array.clear(monthlyBearIFVGs)
    array.clear(weeklyBullIFVGs)
    array.clear(weeklyBearIFVGs)
    array.clear(dailyBullIFVGs)
    array.clear(dailyBearIFVGs)
    array.clear(h4BullIFVGs)
    array.clear(h4BearIFVGs)
    array.clear(h1BullIFVGs)
    array.clear(h1BearIFVGs)
    array.clear(m15BullIFVGs)
    array.clear(m15BearIFVGs)
    array.clear(m5BullIFVGs)
    array.clear(m5BearIFVGs)
    array.clear(chartTFBullIFVGs)
    array.clear(chartTFBearIFVGs)
   
    // Clear terminated FVG arrays
    array.clear(monthlyTerminatedFVGs)
    array.clear(weeklyTerminatedFVGs)
    array.clear(dailyTerminatedFVGs)
    array.clear(h4TerminatedFVGs)
    array.clear(h1TerminatedFVGs)
    array.clear(m15TerminatedFVGs)
    array.clear(m5TerminatedFVGs)
    array.clear(chartTFTerminatedFVGs)

// Helper function to limit FVG arrays
limitFVGArrays() =>
    while array.size(monthlyBullFVGs) > fvgMaxPerTF
        box.delete(array.shift(monthlyBullFVGs))
    while array.size(monthlyBearFVGs) > fvgMaxPerTF
        box.delete(array.shift(monthlyBearFVGs))
    while array.size(weeklyBullFVGs) > fvgMaxPerTF
        box.delete(array.shift(weeklyBullFVGs))
    while array.size(weeklyBearFVGs) > fvgMaxPerTF
        box.delete(array.shift(weeklyBearFVGs))
    while array.size(dailyBullFVGs) > fvgMaxPerTF
        box.delete(array.shift(dailyBullFVGs))
    while array.size(dailyBearFVGs) > fvgMaxPerTF
        box.delete(array.shift(dailyBearFVGs))
    while array.size(h4BullFVGs) > fvgMaxPerTF
        box.delete(array.shift(h4BullFVGs))
    while array.size(h4BearFVGs) > fvgMaxPerTF
        box.delete(array.shift(h4BearFVGs))
    while array.size(h1BullFVGs) > fvgMaxPerTF
        box.delete(array.shift(h1BullFVGs))
    while array.size(h1BearFVGs) > fvgMaxPerTF
        box.delete(array.shift(h1BearFVGs))
    while array.size(m15BullFVGs) > fvgMaxPerTF
        box.delete(array.shift(m15BullFVGs))
    while array.size(m15BearFVGs) > fvgMaxPerTF
        box.delete(array.shift(m15BearFVGs))
    while array.size(m5BullFVGs) > fvgMaxPerTF
        box.delete(array.shift(m5BullFVGs))
    while array.size(m5BearFVGs) > fvgMaxPerTF
        box.delete(array.shift(m5BearFVGs))
    while array.size(chartTFBullFVGs) > fvgMaxPerTF
        box.delete(array.shift(chartTFBullFVGs))
    while array.size(chartTFBearFVGs) > fvgMaxPerTF
        box.delete(array.shift(chartTFBearFVGs))

    // Limit IFVG arrays
    while array.size(monthlyBullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(monthlyBullIFVGs))
    while array.size(monthlyBearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(monthlyBearIFVGs))
    while array.size(weeklyBullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(weeklyBullIFVGs))
    while array.size(weeklyBearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(weeklyBearIFVGs))
    while array.size(dailyBullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(dailyBullIFVGs))
    while array.size(dailyBearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(dailyBearIFVGs))
    while array.size(h4BullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(h4BullIFVGs))
    while array.size(h4BearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(h4BearIFVGs))
    while array.size(h1BullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(h1BullIFVGs))
    while array.size(h1BearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(h1BearIFVGs))
    while array.size(m15BullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(m15BullIFVGs))
    while array.size(m15BearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(m15BearIFVGs))
    while array.size(m5BullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(m5BullIFVGs))
    while array.size(m5BearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(m5BearIFVGs))
    while array.size(chartTFBullIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(chartTFBullIFVGs))
    while array.size(chartTFBearIFVGs) > ifvgMaxPerTF
        box.delete(array.shift(chartTFBearIFVGs))

// Limit FVG arrays to prevent overcrowding
limitFVGArrays()

// Get current bar time for each timeframe
monthlyTime = request.security(syminfo.tickerid, "M", time, lookahead=barmerge.lookahead_off)
weeklyTime = request.security(syminfo.tickerid, "W", time, lookahead=barmerge.lookahead_off)
dailyTime = request.security(syminfo.tickerid, "D", time, lookahead=barmerge.lookahead_off)
h4Time = request.security(syminfo.tickerid, "240", time, lookahead=barmerge.lookahead_off)
h1Time = request.security(syminfo.tickerid, "60", time, lookahead=barmerge.lookahead_off)
m15Time = request.security(syminfo.tickerid, "15", time, lookahead=barmerge.lookahead_off)
m5Time = request.security(syminfo.tickerid, "5", time, lookahead=barmerge.lookahead_off)

// Monthly FVGs - only process on new monthly bars
if (showMonthlyFVG or showMonthlyIFVG) and (monthlyTime != lastMonthlyBar)
    lastMonthlyBar := monthlyTime
    [monthlyBullFVGs, monthlyBearFVGs, monthlyBullIFVGs, monthlyBearIFVGs] = getFVGs("M", monthlyBullIFVGs, monthlyBearIFVGs, monthlyTerminatedFVGs)

// Weekly FVGs - only process on new weekly bars
if (showWeeklyFVG or showWeeklyIFVG) and (weeklyTime != lastWeeklyBar)
    lastWeeklyBar := weeklyTime
    [weeklyBullFVGs, weeklyBearFVGs, weeklyBullIFVGs, weeklyBearIFVGs] = getFVGs("W", weeklyBullIFVGs, weeklyBearIFVGs, weeklyTerminatedFVGs)

// Daily FVGs - only process on new daily bars
if (showDailyFVG or showDailyIFVG) and (dailyTime != lastDailyBar)
    lastDailyBar := dailyTime
    [dailyBullFVGs, dailyBearFVGs, dailyBullIFVGs, dailyBearIFVGs] = getFVGs("D", dailyBullIFVGs, dailyBearIFVGs, dailyTerminatedFVGs)

// 4H FVGs - only process on new 4H bars
if (show4HFVG or show4HIFVG) and (h4Time != lastH4Bar)
    lastH4Bar := h4Time
    [h4BullFVGs, h4BearFVGs, h4BullIFVGs, h4BearIFVGs] = getFVGs("240", h4BullIFVGs, h4BearIFVGs, h4TerminatedFVGs)

// 1H FVGs - only process on new 1H bars
if (show1HFVG or show1HIFVG) and (h1Time != lastH1Bar)
    lastH1Bar := h1Time
    [h1BullFVGs, h1BearFVGs, h1BullIFVGs, h1BearIFVGs] = getFVGs("60", h1BullIFVGs, h1BearIFVGs, h1TerminatedFVGs)

// 15M FVGs - only process on new 15M bars
if (show15MFVG or show15MIFVG) and (m15Time != last15MBar)
    last15MBar := m15Time
    [m15BullFVGs, m15BearFVGs, m15BullIFVGs, m15BearIFVGs] = getFVGs("15", m15BullIFVGs, m15BearIFVGs, m15TerminatedFVGs)

// 5M FVGs - only process on new 5M bars
if (show5MFVG or show5MIFVG) and (m5Time != last5MBar)
    last5MBar := m5Time
    [m5BullFVGs, m5BearFVGs, m5BullIFVGs, m5BearIFVGs] = getFVGs("5", m5BullIFVGs, m5BearIFVGs, m5TerminatedFVGs)
   
// Chart Timeframe FVGs
if (showChartTFFVG or showChartTFIFVG)
    [chartTFBullFVGs, chartTFBearFVGs, chartTFBullIFVGs, chartTFBearIFVGs] = getFVGs(timeframe.period, chartTFBullIFVGs, chartTFBearIFVGs, chartTFTerminatedFVGs)


if barstate.islast
    // Track current row for dynamic table sizing
    var int currentRow = 0
    currentRow := 0
   
    // Headers with dynamic text size - using color.new for more control
    table.cell(stateTable, 0, currentRow, "TF", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, "━━━ STATE ━━━", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, "━━━ TREND ━━━", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1    
   
    // Monthly
    table.cell(stateTable, 0, currentRow, "M", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, stateMonthly, bgcolor=getStateColor(stateMonthly), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(stateMonthly), bgcolor=getStateColor(stateMonthly), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1

    // Weekly
    table.cell(stateTable, 0, currentRow, "W", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, stateWeekly, bgcolor=getStateColor(stateWeekly), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(stateWeekly), bgcolor=getStateColor(stateWeekly), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1
   
    // Daily
    table.cell(stateTable, 0, currentRow, "D", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, stateDaily, bgcolor=getStateColor(stateDaily), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(stateDaily), bgcolor=getStateColor(stateDaily), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1

    // 4H
    table.cell(stateTable, 0, currentRow, "4H", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, state4H, bgcolor=getStateColor(state4H), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(state4H), bgcolor=getStateColor(state4H), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1

    // 1H
    table.cell(stateTable, 0, currentRow, "1H", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, state1H, bgcolor=getStateColor(state1H), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(state1H), bgcolor=getStateColor(state1H), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1
   
    // 15M
    table.cell(stateTable, 0, currentRow, "15M", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, state15M, bgcolor=getStateColor(state15M), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(state15M), bgcolor=getStateColor(state15M), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1
   
    // 5M
    table.cell(stateTable, 0, currentRow, "5M", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, state5M, bgcolor=getStateColor(state5M), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, getTrendText(state5M), bgcolor=getStateColor(state5M), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1

    // Add a blank row for spacing
    currentRow := currentRow + 1
   
    // Opportunity Headers - using color.new for more control
    table.cell(stateTable, 0, currentRow, "OPP", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 1, currentRow, "━━━ ANALYSIS ━━━", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    table.cell(stateTable, 2, currentRow, "━━━ ENTRY ━━━", bgcolor=color.new(HEADER_BG, headerBgTransparency), text_color=color.new(headerTextColor, 0), text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
    currentRow := currentRow + 1
   
    // Process and display signals with dynamic text size
    // Monthly-Weekly
    mw_signal = getOpportunityStrength(stateMonthly, stateWeekly)
    if mw_signal != ""
        table.cell(stateTable, 0, currentRow, "Monthly-Weekly", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, mw_signal, bgcolor=getOpportunityColor(mw_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("Monthly-Weekly", str.contains(mw_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(mw_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1


    // Weekly-Daily
    wd_signal = getOpportunityStrength(stateWeekly, stateDaily)
    if wd_signal != ""
        table.cell(stateTable, 0, currentRow, "Weekly-Daily", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, wd_signal, bgcolor=getOpportunityColor(wd_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("Weekly-Daily", str.contains(wd_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(wd_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1
   
    // Daily-4H
    d4h_signal = getOpportunityStrength(stateDaily, state4H)
    if d4h_signal != ""
        table.cell(stateTable, 0, currentRow, "Daily-4H", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, d4h_signal, bgcolor=getOpportunityColor(d4h_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("Daily-4H", str.contains(d4h_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(d4h_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1
   
    // 4H-1H
    h4h1_signal = getOpportunityStrength(state4H, state1H)
    if h4h1_signal != ""
        table.cell(stateTable, 0, currentRow, "4H-1H", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, h4h1_signal, bgcolor=getOpportunityColor(h4h1_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("4H-1H", str.contains(h4h1_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(h4h1_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1


    // 1H-15M
    h1m15_signal = getOpportunityStrength(state1H, state15M)
    if h1m15_signal != ""
        table.cell(stateTable, 0, currentRow, "1H-15M", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, h1m15_signal, bgcolor=getOpportunityColor(h1m15_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("1H-15M", str.contains(h1m15_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(h1m15_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1
   
    // 15M-5M
    m15m5_signal = getOpportunityStrength(state15M, state5M)
    if m15m5_signal != ""
        table.cell(stateTable, 0, currentRow, "15M-5M", bgcolor=color.new(color.gray, cellBgTransparency), text_color=textColor, text_halign=text.align_right, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 1, currentRow, m15m5_signal, bgcolor=getOpportunityColor(m15m5_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        table.cell(stateTable, 2, currentRow, getEntryPoint("15M-5M", str.contains(m15m5_signal, "▲") ? "▲" : "▼"), bgcolor=getOpportunityColor(m15m5_signal), text_color=textColor, text_halign=text.align_center, text_size=getTableTextSize(tableTextSize))
        currentRow := currentRow + 1

