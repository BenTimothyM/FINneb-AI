
# FINNEB AI: Agentic Financial Assistant Terminal Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Rich](https://img.shields.io/badge/UI-Rich_TUI-orange?style=for-the-badge)

**FINNEB AI** is an advanced, high-fidelity Terminal User Interface (TUI) dashboard designed to act as an autonomous agentic financial assistant. It bridges quantitative market data, real-time narrative sentiment parsing, and cutting-edge generative AI reasoning into a centralized, sleek command-line terminal. 

The application aggregates asset analytics across multiple asset classes (Equities, Forex, and Cryptocurrencies) and generates comprehensive, investment-grade cognitive strategy reports powered by the Google Gemini API.

---

## ✨ Key Features

- 📈 **Multi-Asset Ingestion Pipeline:** Seamlessly switches extraction pipelines between traditional equities/FX (via Alpha Vantage, Finnhub, and `yfinance`) and digital assets (via the `CCXT` gateway).
- 🧠 **Dual-Compatible Cognitive Engine:** Fully supports both the legacy Google Generative AI SDK and the modern, unified `google-genai` client using automated fallback detection to generate deep financial evaluations.
- 📰 **Heuristic Sentiment Aggregator:** Scrapes real-time headlines from Alpha Vantage News Sentiment clusters or parses Google News RSS fields to generate algorithmic directional sentiment indexes (Bullish/Bearish/Neutral).
- 🗄️ **Local Archival & Reporting System:** Automatically logs every successful ticker analysis into a local SQLite database vault and dynamically appends formatted rows into an offline Excel tracking worksheet.
- 🎨 **High-Fidelity TUI:** Utilizes the `Rich` terminal engine to deliver structural layouts, clear metrics tables, real-time application log streaming, and beautiful Markdown report parsing.

---

## 💻 Tech Stack & Integrations

- **Core Architecture:** Python 3.9+
- **Data Providers:** Alpha Vantage, Finnhub, Yahoo Finance (`yfinance`)
- **Crypto Gateway:** CCXT (CryptoCurrency eXchange Trading library)
- **AI Reasoning:** Google Gemini API (`gemini-2.5-flash` default)
- **TUI & Rendering:** Rich Framework
- **Storage Engines:** SQLite3, Pandas, OpenPyXL (Excel integration)

---

## 🚀 Getting Started & Installation

Follow these precise steps to set up the environment, configure API integrations, and run the dashboard application.

### 1. Prerequisites & Python Version
Ensure you have **Python 3.9 or higher** installed on your system. You can verify your local installation by running:
```bash
python --version

```

### 2. Set Up a Virtual Environment (Recommended)

Isolate dependencies by creating and activating a standard Python virtual environment (`venv`).

* **Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate

```


* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

Install all the required functional libraries using the provided requirements tracking file:

```bash
pip install -r requirements.txt

```

### 4. Configure Environment Variables (`.env`)

Create a file named `.env` in the root directory of the project and populate it with your respective API credentials using the structure below:

```env
# ==============================================================================
# FINNEB AI - API KEY CONFIGURATION ENGINE
# ==============================================================================

# Gemini API Key (Generate at Google AI Studio)
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Choose model: 'gemini-2.5-pro' (high precision) or 'gemini-2.5-flash' (low-latency)
GEMINI_MODEL="gemini-2.5-flash"

# Alpha Vantage API Key (Generate at alphavantage.co)
ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_API_KEY"

# Finnhub API Key (Generate at finnhub.io)
FINNHUB_API_KEY="YOUR_FINNHUB_API_KEY"

# ==============================================================================
# CCXT CRYPTO EXCHANGE CONFIGURATION
# ==============================================================================
# (default: binance)
CCXT_EXCHANGE="binance"

```

---

## 🛠️ Advanced Customization & CCXT Troubleshooting

The application queries data through the exchange specified in `CCXT_EXCHANGE`. If you encounter network timeouts, localized connection blocks, or API errors related to your native exchange driver, you can seamlessly swap the underlying router.

> ⚠️ **Important Exchange Verification Note:**
> To ensure your machine supports a specific crypto exchange driver, run the auxiliary validation script (`check_exchanges.py`) that will be provided in your project workspace. This script lists all the certified and functional exchange engines supported by CCXT on your system.
> If `binance` fails, simply update your configuration to a working alternative (e.g., `coinbase`, `kraken`, or `okx`):
> ```env
> CCXT_EXCHANGE="coinbase"
> 
> ```
> 
> 

---

## 💡 How to Use

Once your virtual environment is active and your API tokens are completely set up inside the `.env` container, launch the dashboard terminal:

```bash
python main.py

```

### Navigating the Interface:

1. Upon initialization, the terminal will render a clean system status header banner.
2. Enter your desired ticker asset when prompted at the input line (`>> `):
* **Equities:** `AAPL`, `TSLA`, `MSFT`
* **Cryptocurrencies:** `BTC/USDT`, `ETH/USDT`, or simply `SOL`, `ADA`


3. The background agent will execute extraction, run AI model synthesis, update the system ledger records (`finneb_ai_vault.db` & `finneb_reports.xlsx`), and print out a dense analytics report dashboard.
4. Type `exit` or `quit` to cleanly shut down the dashboard execution frame.

---

## 👨‍💻 Credits

This project is developed and maintained by:

* **Ben Timothy** - [@BenTimothyM](https://github.com/BenTimothyM)

## 📜 License

This project is distributed under the **MIT License**. See the `LICENSE` file for more details.
