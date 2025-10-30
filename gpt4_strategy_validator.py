"""
GPT-4 Strategy Validator
Provides AI-powered analysis and validation of trading strategy selections
"""

import os
import json
from openai import OpenAI

def validate_strategy(strategy_data, prop_firm_rules, all_strategies):
    """
    Use GPT-4 to analyze and validate the selected trading strategy
    
    Args:
        strategy_data: Dict containing the top strategy's metrics
        prop_firm_rules: Dict containing the prop firm rules being optimized for
        all_strategies: List of alternative strategies for comparison
    
    Returns:
        Dict containing GPT-4's analysis and recommendation
    """
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Prepare the analysis prompt
    prompt = f"""You are an expert quantitative trading analyst specializing in futures prop firm evaluations. 
Analyze the following trading strategy selection and provide your professional assessment.

**SELECTED STRATEGY:**
- Sessions: {strategy_data['sessions']}
- Time Filter: {strategy_data['timeFilter']}
- Break Even Strategy: {strategy_data['beStrategy']}
- R-Target: {strategy_data['rTarget']}R
- Risk Per Trade: {strategy_data['riskPerTrade']}%

**PERFORMANCE METRICS:**
- Expectancy: {strategy_data['expectancy']}R
- Win Rate: {strategy_data['winRate']}%
- Expected Return: {strategy_data['expectedReturn']}%
- Max Daily Loss: {strategy_data['maxDailyLoss']}%
- Max Drawdown: {strategy_data['maxDrawdown']}%
- Total Trades: {strategy_data['totalTrades']}
- Profit Factor: {strategy_data.get('profitFactor', 'N/A')}

**PROP FIRM REQUIREMENTS:**
{json.dumps(prop_firm_rules, indent=2)}

**ALTERNATIVE STRATEGIES AVAILABLE:**
Top 3 alternatives with different risk/reward profiles exist.

**YOUR TASK:**
1. Assess whether this strategy is appropriate for the given prop firm rules
2. Identify the key strengths that make this strategy suitable
3. Highlight any potential concerns or risks
4. Provide a confidence score (1-10) on whether you agree with this selection
5. Suggest any modifications or considerations for the trader

Be concise but thorough. Focus on practical trading insights, not generic advice."""

    try:
        # Call GPT-4 API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert quantitative trading analyst with deep knowledge of prop firm trading, risk management, and strategy optimization. Provide clear, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "success": True,
            "analysis": analysis,
            "model": "gpt-4",
            "timestamp": None  # Will be set by backend
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis": "Unable to generate AI analysis at this time. Please ensure your OpenAI API key is configured."
        }


def format_analysis_for_display(analysis_result):
    """
    Format the GPT-4 analysis for HTML display
    
    Args:
        analysis_result: Dict containing the analysis from GPT-4
    
    Returns:
        HTML string for display
    """
    
    if not analysis_result.get("success"):
        return f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 16px;">
            <p style="margin: 0; color: #ef4444;">⚠️ AI Analysis Unavailable: {analysis_result.get('error', 'Unknown error')}</p>
        </div>
        """
    
    analysis_text = analysis_result.get("analysis", "")
    
    return f"""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1)); border: 2px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 20px; margin-top: 20px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="font-size: 2rem;">🤖</div>
            <div>
                <h3 style="margin: 0; color: #8b5cf6; font-size: 1.25rem;">GPT-4 Strategy Analysis</h3>
                <p style="margin: 4px 0 0 0; color: var(--text-secondary); font-size: 0.875rem;">Independent AI validation of strategy selection</p>
            </div>
        </div>
        <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 16px; line-height: 1.8; color: var(--text-primary); white-space: pre-wrap;">
{analysis_text}
        </div>
        <p style="margin: 12px 0 0 0; color: var(--text-secondary); font-size: 0.75rem; font-style: italic;">
            Powered by OpenAI GPT-4 • Analysis generated in real-time
        </p>
    </div>
    """
