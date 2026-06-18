import os
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.padding import Padding

def clear_terminal():
    """Completely clearing the entire screen buffer using the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

class TerminalUIEngine:
    """Constructs the high-fidelity terminal layout structure."""
    @staticmethod
    def get_ascii_banner() -> str:
        return """  ███████╗██╗███╗   ██╗███╗   ██╗███████╗██████╗      █████╗ ██╗
  ██╔════╝██║████╗  ██║████╗  ██║██╔════╝██╔══██╗    ██╔══██╗██║
  █████╗  ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝    ███████║██║
  ██╔══╝  ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗    ██╔══██║██║
  ██║     ██║██║ ╚████║██║ ╚████║███████╗██████╔╝    ██║  ██║██║
  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═════╝     ╚═╝  ╚═╝╚═╝"""

    @staticmethod
    def get_status_bar() -> Text:
        status_text = Text()
        status_text.append("[ ", style="bright_blue")
        status_text.append("SYSTEM STATUS: ONLINE", style="orange3 bold")
        status_text.append(" ]   [ ", style="bright_blue")
        status_text.append("VERSION: 1.0.0", style="orange3 bold")
        status_text.append(" ]  [ ", style="bright_blue")
        status_text.append("REGION: GLOBAL", style="orange3 bold")
        status_text.append(" ]", style="bright_blue")
        return status_text

    def render_dashboard(self, ticker: str, price_data: dict, news_items: list, ai_report: str, log_stream: list) -> Layout:
        header_text = Text()
        header_text.append("\n")
        header_text.append(self.get_ascii_banner(), style="bold bright_cyan")
        header_text.append("\n" + "=" * 66 + "\n", style="bright_blue")
        header_text.append(self.get_status_bar())
        header_text.append("\n" + "-" * 66, style="bright_black")

        header_panel = Padding(header_text, (0, 2))

        metrics_table = Table(show_header=True, header_style="bold cyan", box=None)
        metrics_table.add_column("Asset Metric", style="bold white", width=22)
        metrics_table.add_column("Metric Value", style="bright_green", justify="right")

        cp = price_data.get("current_price")
        chg = price_data.get("change_pct", 0.0)
        chg_style = "bright_green" if chg >= 0 else "bright_red"
        
        p_str = f"${cp:,.4f}" if isinstance(cp, (int, float)) else "N/A"
        sma20_str = f"${price_data.get('sma_20'):,.4f}" if price_data.get('sma_20') else "N/A"
        sma50_str = f"${price_data.get('sma_50'):,.4f}" if price_data.get('sma_50') else "N/A"
        vol_str = f"{price_data.get('volatility', 0.0) * 100:.2f}%" if price_data.get('volatility') else "N/A"
        vol_num = price_data.get("volume")
        vol_fmt = f"{vol_num:,.0f}" if isinstance(vol_num, (int, float)) else "N/A"

        metrics_table.add_row("Current Valuation", p_str)
        metrics_table.add_row("Daily Shift %", f"{chg:+.2f}%", style=chg_style)
        metrics_table.add_row("Market Volume", vol_fmt)
        metrics_table.add_row("Simple Moving Avg (20)", sma20_str)
        metrics_table.add_row("Simple Moving Avg (50)", sma50_str)
        metrics_table.add_row("30D Ann. Volatility", vol_str)

        left_panel = Panel(
            metrics_table,
            title=f"[bold bright_cyan] QUANTITATIVE METRICS ({ticker.upper()}) [/bold bright_cyan]",
            border_style="bright_blue",
            expand=True
        )

        news_table = Table(show_header=True, header_style="bold cyan", box=None)
        news_table.add_column("Source", style="bright_black", width=12)
        news_table.add_column("Headlines", style="bright_white", ratio=3)
        news_table.add_column("Sentiment Index", justify="center", ratio=1)

        for item in news_items[:4]:
            sent = item.get("sentiment", "NEUTRAL")
            if sent == "BULLISH":
                sent_badge = "[bold black on bright_green]  BULLISH  [/bold black on bright_green]"
            elif sent == "BEARISH":
                sent_badge = "[bold black on bright_red]  BEARISH  [/bold black on bright_red]"
            else:
                sent_badge = "[bold black on white]  NEUTRAL  [/bold black on white]"

            title_txt = item.get("title", "")
            if len(title_txt) > 60:
                title_txt = title_txt[:57] + "..."

            news_table.add_row(item.get("source", "N/A"), title_txt, sent_badge)

        right_top_panel = Panel(
            news_table,
            title="[bold bright_cyan] REAL-TIME NEWS AGGREGATOR [/bold bright_cyan]",
            border_style="bright_blue",
            expand=True
        )

        main_layout = Layout()
        main_layout.split_column(
            Layout(header_panel, name="header", size=9),
            Layout(name="body", ratio=1),
        )

        main_layout["body"].split_row(
            Layout(left_panel, name="left", ratio=1),
            Layout(name="right", ratio=2)
        )

        main_layout["right"].split_column(
            Layout(right_top_panel, name="news", ratio=1),
        )

        return main_layout