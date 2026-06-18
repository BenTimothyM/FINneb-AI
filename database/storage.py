import os
import datetime
import sqlite3
import pandas as pd

class DBManager:
    """Handles local archival of analytical logs to SQLite databases."""
    def __init__(self, db_path="finneb_ai_vault.db"):
        self.db_path = db_path
        self._init_sqlite()

    def _init_sqlite(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        ticker TEXT,
                        price REAL,
                        change_pct REAL,
                        volume REAL,
                        sma_20 REAL,
                        sma_50 REAL,
                        volatility REAL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS news_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        ticker TEXT,
                        title TEXT,
                        source TEXT,
                        sentiment TEXT,
                        score REAL
                    )
                """)
                conn.commit()
        except Exception:
            pass

    def save_records(self, ticker: str, price_data: dict, news_items: list):
        """Commits data to SQLite database."""
        now = datetime.datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO price_history (timestamp, ticker, price, change_pct, volume, sma_20, sma_50, volatility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    now,
                    ticker.upper(),
                    price_data.get("current_price"),
                    price_data.get("change_pct"),
                    price_data.get("volume"),
                    price_data.get("sma_20"),
                    price_data.get("sma_50"),
                    price_data.get("volatility")
                ))

                for item in news_items:
                    cursor.execute("""
                        INSERT INTO news_history (timestamp, ticker, title, source, sentiment, score)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        now,
                        ticker.upper(),
                        item.get("title"),
                        item.get("source"),
                        item.get("sentiment"),
                        item.get("score")
                    ))
                conn.commit()
        except Exception:
            pass


def export_to_excel(ticker: str, price_data: dict, news_items: list, filename="finneb_reports.xlsx"):
    """Appends records to Excel sheets without overwriting prior records."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    price_row = {
        "Timestamp": [now],
        "Ticker": [ticker.upper()],
        "Price": [price_data.get("current_price")],
        "Change %": [price_data.get("change_pct")],
        "Volume": [price_data.get("volume")],
        "SMA_20": [price_data.get("sma_20")],
        "SMA_50": [price_data.get("sma_50")],
        "Volatility (30D)": [price_data.get("volatility")]
    }
    df_price = pd.DataFrame(price_row)
    
    news_rows = []
    for item in news_items:
        news_rows.append({
            "Timestamp": now,
            "Ticker": ticker.upper(),
            "Title": item.get("title"),
            "Source": item.get("source"),
            "Sentiment": item.get("sentiment"),
            "Score": item.get("score")
        })
    df_news = pd.DataFrame(news_rows)
    
    try:
        if os.path.exists(filename):
            with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                for sheet_name, df_to_write in [("Price History", df_price), ("News Sentiment", df_news)]:
                    try:
                        startrow = writer.sheets[sheet_name].max_row
                    except KeyError:
                        startrow = 0
                    header = True if startrow == 0 else False
                    df_to_write.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False, header=header)
        else:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_price.to_excel(writer, sheet_name="Price History", index=False)
                df_news.to_excel(writer, sheet_name="News Sentiment", index=False)
    except Exception:
        pass