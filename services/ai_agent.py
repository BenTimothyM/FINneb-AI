import os
from config.settings import USING_NEW_SDK, genai_client, genai_legacy

class FinancialAnalystAgent:
    """Executes high-grade cognitive reasoning reports through the Gemini API."""
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_choice = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if self.api_key and USING_NEW_SDK:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)

    def generate_report(self, ticker: str, price_data: dict, news_items: list, logger_func) -> str:
        if not self.api_key:
            logger_func("No Gemini API key detected. Deploying heuristic simulation engine...")
            return self._heuristic_report(ticker, price_data)

        try:
            logger_func(f"Context compiled. Dispatching request to Gemini model ({self.model_choice})...")
            
            prompt = f"""
            Act as an elite Senior Quantitative Analyst and Investment Strategist.
            You are evaluating the target asset: {ticker.upper()}.
            
            --- QUANTITATIVE METRICS ---
            - Current Valuation: {price_data.get('current_price')}
            - Volatility Metric (30D Annualized): {price_data.get('volatility')}
            - Simple Moving Average (20D): {price_data.get('sma_20')}
            - Simple Moving Average (50D): {price_data.get('sma_50')}
            
            --- RECENT HEADLINES & RECONSTRUCTED SENTIMENT ---
            {news_items}
            
            Provide a sophisticated, clear, and action-oriented financial report in Markdown formatting containing:
            1. **Market Condition Breakdown**: Analyze volatility and price relation to SMA-20 and SMA-50 lines.
            2. **Qualitative Sentiment Analysis**: Synthesize raw headlines, mapping institutional narrative trajectory.
            3. **Short-Term Directional Outlook**: A strategic hypothesis including critical pivot levels.
            
            --- CRITICAL RENDERING RULES ---
            1. DO NOT output any introductory title, subtitle, header, date lines, or bracketed placeholders (such as "SOL/USDT - Strategic Quantitative & Sentiment Analysis" or "Current Date").
            2. Start the analysis directly with the first section: "1. Market Condition Breakdown" or "### 1. Market Condition Breakdown".
            3. Ensure structure is clean, objective, and dense with professional financial terminology. Keep details compact so it fits beautifully in the dashboard.
            """
            
            if USING_NEW_SDK and self.client:
                response = self.client.models.generate_content(
                    model=self.model_choice,
                    contents=prompt
                )
                return response.text
            elif not USING_NEW_SDK and genai_legacy:
                model = genai_legacy.GenerativeModel(self.model_choice)
                response = model.generate_content(prompt)
                return response.text
            else:
                return "### SDK Import Failure\nNeither the legacy google-generativeai nor the new google-genai libraries were initialized."
        except Exception as e:
            return f"### AI Pipeline Execution Error\n{str(e)}"

    def _heuristic_report(self, ticker: str, price_data: dict) -> str:
        current_price = price_data.get("current_price", 0.0)
        sma20 = price_data.get("sma_20", 0.0)
        
        trend = "Bullish Outperformance" if (sma20 and current_price > sma20) else "Bearish Convergence"
        
        return f"""### 1. Market Condition Breakdown
- **Trend Index**: Currently demonstrating a **{trend}** pattern.
- **Volatility Parameters**: Metric limits show moderate consolidation.

### 2. Qualitative Sentiment Analysis
- Headwinds and narrative indicators remain structurally neutral. Portfolio distribution actions show standard reassignment.

### 3. Short-Term Directional Outlook
- **Support Target**: {current_price * 0.97:.2f} if applicable
- **Resistance Level**: {current_price * 1.03:.2f} if applicable
- **Baseline Forecast**: Continued flat consolidation pending high-volume break events.
"""