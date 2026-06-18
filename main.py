import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

# Impor modul lokal hasil pemisahan
from database.storage import DBManager, export_to_excel
from services.market_data import MarketDataIngestor
from services.sentiment import NewsSentimentEngine
from services.ai_agent import FinancialAnalystAgent
from ui.terminal import TerminalUIEngine, clear_terminal

# Global Console Instantiation
console = Console()

def main():
    db = DBManager()
    ingestor = MarketDataIngestor()
    news_engine = NewsSentimentEngine()
    analyst = FinancialAnalystAgent()
    ui = TerminalUIEngine()

    logs = ["Engine successfully booted. Terminal initialized."]

    def add_log(msg: str):
        logs.append(msg)
        if len(logs) > 30:
            logs.pop(0)

    while True:
        clear_terminal()
        
        banner_content = ui.get_ascii_banner()
        
        startup_text = Text()
        startup_text.append("\n")  
        startup_text.append(banner_content, style="bold bright_cyan")
        startup_text.append("\n" + "=" * 66 + "\n", style="bright_blue")
        startup_text.append(ui.get_status_bar())
        startup_text.append("\n" + "-" * 66 + "\n", style="bright_black")
        
        console.print(startup_text)
        
        console.print("[bold yellow]Enter ticker symbol to parse (e.g., AAPL, TSLA, BTC/USDT) or 'exit' to quit:[/bold yellow]")
        ticker_input = input(">> ").strip()

        if not ticker_input:
            continue
        if ticker_input.lower() in ["exit", "quit"]:
            console.print("\nExiting FINNEB AI. Goodbye.\n", style="bold red")
            sys.exit(0)

        add_log(f"Aggregating quantitative dataset: {ticker_input.upper()}")
        
        price_data = ingestor.fetch_market_data(ticker_input, add_log)
        
        if not price_data or not price_data.get("current_price"):
            add_log(f"Incomplete data retrieved for ticker: {ticker_input.upper()}")
            console.print(f"\n[bold red]Error: Could not retrieve market pricing for '{ticker_input}'. Check spelling or connection.[/bold red]\n")
            input("Press Enter to continue...")
            continue

        add_log(f"Executing sentiment scraping: {ticker_input.upper()}")
        news_items = news_engine.fetch_news_dataset(ticker_input, add_log)

        add_log(f"Executing Gemini cognitive engine model: {ticker_input.upper()}")
        report = analyst.generate_report(ticker_input, price_data, news_items, add_log)

        add_log(f"Archiving processed values into SQLite local database...")
        db.save_records(ticker_input, price_data, news_items)
        
        add_log(f"Writing log entries to offline Excel tracking file...")
        export_to_excel(ticker_input, price_data, news_items)
        
        dashboard_layout = ui.render_dashboard(ticker_input, price_data, news_items, report, logs)
        
        clear_terminal()
        console.print(dashboard_layout)

        print("\n")
        console.print("=" * 90, style="bold bright_magenta")
        console.print(" [bold bright_magenta]GEMINI COGNITIVE ANALYTICS - FULL UNTRUNCATED REPORT[/bold bright_magenta]")
        console.print("=" * 90, style="bold bright_magenta")
        console.print(Markdown(report))
        console.print("=" * 90, style="bold bright_magenta")

        print("\n")
        console.print("[bold yellow]Press Enter to return to main prompt and search a new ticker...[/bold yellow]")
        input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print(" CRITICAL TERMINAL APPLICATION ERROR")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        input("\nAn error occurred. Press ENTER to close this window...")
        sys.exit(1)