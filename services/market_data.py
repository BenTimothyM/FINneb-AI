import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt

class MarketDataIngestor:
    """Aggregates equity, forex, and cryptocurrency market data with multi-source fallback."""
    def __init__(self):
        self.av_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.ccxt_exchange_id = os.getenv("CCXT_EXCHANGE", "binance").lower()

    def fetch_market_data(self, ticker: str, logger_func) -> dict:
        ticker_upper = ticker.upper()
        
        if "/" in ticker_upper or ticker_upper in ["BTC", "ETH", "SOL", "ADA", "XRP", "DOT"]:
            logger_func(f"Crypto asset class identified. Accessing CCXT Gateway ({self.ccxt_exchange_id})...")
            return self._fetch_crypto_ccxt(ticker_upper, logger_func)
        
        logger_func(f"Equity/FX asset class identified. Launching Alpha Vantage primary parser...")
        return self._fetch_equity_unified(ticker_upper, logger_func)

    def _fetch_crypto_ccxt(self, ticker: str, logger_func) -> dict:
        try:
            if hasattr(ccxt, self.ccxt_exchange_id):
                exchange_class = getattr(ccxt, self.ccxt_exchange_id)
                exchange = exchange_class({'enableRateLimit': True})
            else:
                logger_func(f"Exchange '{self.ccxt_exchange_id}' not found in CCXT. Falling back to binance.")
                exchange = ccxt.binance({'enableRateLimit': True})
            
            symbol = ticker if "/" in ticker else f"{ticker}/USDT"
            
            ticker_data = exchange.fetch_ticker(symbol)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=100)
            
            df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
            
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['Daily_Return'] = df['Close'].pct_change()
            
            volatility = float(df['Daily_Return'].std() * np.sqrt(252))
            current_price = float(ticker_data.get('last', df['Close'].iloc[-1]))
            change_pct = float(ticker_data.get('percentage', 0.0))
            volume = float(ticker_data.get('baseVolume', df['Volume'].iloc[-1]))
            
            return {
                "current_price": current_price,
                "change_pct": change_pct,
                "volume": volume,
                "sma_20": float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None,
                "sma_50": float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None,
                "volatility": volatility if not pd.isna(volatility) else 0.0
            }
        except Exception:
            logger_func("CCXT connection error. Trying yfinance backup...")
            return self._fallback_yfinance(ticker.replace("/", "-"))

    def _fetch_equity_unified(self, ticker: str, logger_func) -> dict:
        data = {
            "current_price": None,
            "change_pct": 0.0,
            "volume": None,
            "sma_20": None,
            "sma_50": None,
            "volatility": 0.0
        }
        
        try:
            df = yf.download(ticker, period="3mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()
                df['Daily_Return'] = df['Close'].pct_change()
                
                data["volatility"] = float(df['Daily_Return'].std() * np.sqrt(252))
                data["sma_20"] = float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None
                data["sma_50"] = float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None
                data["current_price"] = float(df['Close'].iloc[-1])
                data["volume"] = float(df['Volume'].iloc[-1])
                
                if len(df) > 1:
                    prev_close = float(df['Close'].iloc[-2])
                    current_close = float(df['Close'].iloc[-1])
                    data["change_pct"] = ((current_close - prev_close) / prev_close) * 100
        except Exception:
            pass

        av_success = False
        if self.av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={self.av_key}"
                res = requests.get(url, timeout=8)
                res_json = res.json()
                
                if "Note" in res_json or "Information" in res_json:
                    logger_func("Alpha Vantage limit hit. Executing seamless fallback routing...")
                elif "Global Quote" in res_json and res_json["Global Quote"]:
                    gq = res_json["Global Quote"]
                    data["current_price"] = float(gq.get("05. price", data["current_price"]))
                    chg_str = gq.get("10. change percent", "0%")
                    data["change_pct"] = float(chg_str.replace("%", ""))
                    data["volume"] = float(gq.get("06. volume", data["volume"]))
                    av_success = True
            except Exception:
                logger_func("Primary AV request failed. Activating yfinance fallback protocol.")

        if self.finnhub_key and not av_success:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={self.finnhub_key}"
                res = requests.get(url, timeout=8)
                fh_json = res.json()
                if fh_json and "c" in fh_json:
                    data["current_price"] = float(fh_json["c"])
                    data["change_pct"] = float(fh_json.get("dp", data["change_pct"]))
            except Exception:
                pass
                
        return data

    def _fallback_yfinance(self, ticker: str) -> dict:
        try:
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty:
                return {}
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['Daily_Return'] = df['Close'].pct_change()
            
            volatility = float(df['Daily_Return'].std() * np.sqrt(252))
            current_price = float(df['Close'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            change_pct = 0.0
            if len(df) > 1:
                prev_close = float(df['Close'].iloc[-2])
                change_pct = ((current_price - prev_close) / prev_close) * 100

            return {
                "current_price": current_price,
                "change_pct": change_pct,
                "volume": volume,
                "sma_20": float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None,
                "sma_50": float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None,
                "volatility": volatility if not pd.isna(volatility) else 0.0
            }
        except Exception:
            return {}