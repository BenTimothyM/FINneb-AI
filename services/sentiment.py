import os
import requests
import urllib.request
import xml.etree.ElementTree as ET

class NewsSentimentEngine:
    """Retrieves external headlines and aggregates qualitative narrative flags."""
    def __init__(self):
        self.av_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    def fetch_news_dataset(self, ticker: str, logger_func) -> list:
        news_list = []
        
        if self.av_key:
            try:
                logger_func("Calling Alpha Vantage news sentiment cluster...")
                url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={self.av_key}"
                res = requests.get(url, timeout=8)
                av_data = res.json()
                
                if "feed" in av_data:
                    for article in av_data["feed"][:10]:
                        title = article.get("title", "")
                        source = article.get("source", "AV News")
                        score = float(article.get("overall_sentiment_score", 0.0))
                        sentiment = "NEUTRAL"
                        if score >= 0.15: sentiment = "BULLISH"
                        elif score <= -0.15: sentiment = "BEARISH"
                        
                        news_list.append({
                            "title": title,
                            "source": source,
                            "sentiment": sentiment,
                            "score": score
                        })
                    return news_list
            except Exception:
                pass

        logger_func("Executing Google News RSS semantic collector...")
        return self._fetch_google_news(ticker)

    def _fetch_google_news(self, ticker: str) -> list:
        query = ticker.replace("/", " ")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            news_items = []
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text if item.find('title') is not None else "No Title"
                source_elem = item.find('source')
                source = source_elem.text if source_elem is not None else "Google News"
                
                if " - " in title:
                    title = " - ".join(title.split(" - ")[:-1])
                
                news_items.append({
                    "title": title,
                    "source": source,
                    "sentiment": "NEUTRAL",
                    "score": 0.0
                })
            
            return self._calculate_heuristic_sentiment(news_items)
        except Exception:
            return [
                {"title": f"Market pricing adjusts inside expected target margins for {ticker}", "source": "System Core", "sentiment": "NEUTRAL", "score": 0.0},
                {"title": f"Macro conditions and liquidity indicators remain stable", "source": "System Core", "sentiment": "NEUTRAL", "score": 0.0}
            ]

    def _calculate_heuristic_sentiment(self, news_items: list) -> list:
        bullish_terms = {"surge", "rise", "gain", "bold", "jump", "growth", "high", "positive", "up", "rally", "buy"}
        bearish_terms = {"fall", "drop", "decline", "bearish", "loss", "low", "negative", "down", "crash", "sell", "slip"}
        
        for item in news_items:
            title_lower = item["title"].lower()
            bull_ct = sum(1 for word in bullish_terms if word in title_lower)
            bear_ct = sum(1 for word in bearish_terms if word in title_lower)
            
            if bull_ct > bear_ct:
                item["sentiment"] = "BULLISH"
                item["score"] = round(0.5 + (bull_ct * 0.1), 2)
            elif bear_ct > bull_ct:
                item["sentiment"] = "BEARISH"
                item["score"] = round(-0.5 - (bear_ct * 0.1), 2)
            else:
                item["sentiment"] = "NEUTRAL"
                item["score"] = 0.0
        return news_items