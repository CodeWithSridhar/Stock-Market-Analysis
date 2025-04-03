import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import base64
from io import StringIO
import pandas_datareader.data as web
import requests
import json
import time

# Set page configuration
st.set_page_config(
    page_title="Indian Stock Market Analysis",
    page_icon="📈",
    layout="wide"
)

# Create a theme toggle button in the sidebar
theme = st.sidebar.toggle("Dark Theme", value=False)

# Apply theme based on toggle
if theme:
    st.markdown("""
        <style>
        :root {
            --background-color: #0E1117;
            --text-color: #E0E0E0;
            --card-background: #1E1E1E;
        }
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .card {
            background-color: var(--card-background) !important;
            color: var(--text-color) !important;
        }
        .metric-value, .metric-label {
            color: var(--text-color) !important;
        }
        .stButton button {
            background-color: #FF6B6B !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        :root {
            --background-color: #FFFFFF;
            --text-color: #262730;
            --card-background: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session states
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3D5A80;
        margin-bottom: 1rem;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-label {
        color: #3D5A80;
        font-weight: bold;
        font-size: 1rem;
    }
    .metric-value {
        color: #FF6B6B;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 5px solid #FF6B6B;
        padding: 10px;
        border-radius: 0 5px 5px 0;
        margin-bottom: 10px;
    }
    .green-text {
        color: #28a745;
    }
    .red-text {
        color: #dc3545;
    }
    .highlight {
        background-color: #FFE66D;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .download-btn {
        text-align: center;
        color: white;
        background-color: #FF6B6B;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 10px 0;
        transition: background-color 0.3s;
    }
    .download-btn:hover {
        background-color: #FF4F4F;
        text-decoration: none;
        color: white;
    }
    .footer {
        text-align: center;
        margin-top: 20px;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# App title and header
st.markdown('<div class="main-header">🇮🇳 Indian Stock Market Analysis 📊</div>', unsafe_allow_html=True)

# App description in a colorful info box
st.markdown("""
<div class="info-box">
    <p>Enter an Indian stock symbol to view financial data, interactive charts, and download information.</p>
    <p><b>📈 For NSE stocks:</b> Add <span class="highlight">.NS</span> after the symbol (e.g., <code>RELIANCE.NS</code>)</p>
    <p><b>📉 For BSE stocks:</b> Add <span class="highlight">.BO</span> after the symbol (e.g., <code>RELIANCE.BO</code>)</p>
</div>
""", unsafe_allow_html=True)

# Market Overview widget showing major Indian indices
st.markdown('<div class="sub-header">🔍 Market Overview</div>', unsafe_allow_html=True)

# Create a 4-column layout for market indices
col1, col2, col3, col4 = st.columns(4)


# Function to get current index data
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_index_data(ticker):
    try:
        index = yf.Ticker(ticker)
        info = index.info
        current = info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', 0)
        change = current - prev_close
        pct_change = (change / prev_close) * 100 if prev_close else 0
        return current, change, pct_change
    except:
        return 0, 0, 0


# Get data for each index
nifty_price, nifty_change, nifty_pct = get_index_data("^NSEI")  # NIFTY 50
sensex_price, sensex_change, sensex_pct = get_index_data("^BSESN")  # SENSEX
nifty_bank_price, nifty_bank_change, nifty_bank_pct = get_index_data("^NSEBANK")  # NIFTY BANK
nifty_it_price, nifty_it_change, nifty_it_pct = get_index_data("NIFTYIT.NS")  # NIFTY IT

# Display the indices
with col1:
    st.markdown(f"""
    <div class="card" style="text-align: center; height: 100px;">
        <span class="metric-label">NIFTY 50</span>
        <div class="metric-value">{nifty_price:.2f}</div>
        <p class="{'green-text' if nifty_change >= 0 else 'red-text'}" style="margin: 0;">
            {'+' if nifty_change >= 0 else ''}{nifty_change:.2f} ({nifty_pct:.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="text-align: center; height: 100px;">
        <span class="metric-label">SENSEX</span>
        <div class="metric-value">{sensex_price:.2f}</div>
        <p class="{'green-text' if sensex_change >= 0 else 'red-text'}" style="margin: 0;">
            {'+' if sensex_change >= 0 else ''}{sensex_change:.2f} ({sensex_pct:.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="text-align: center; height: 100px;">
        <span class="metric-label">NIFTY BANK</span>
        <div class="metric-value">{nifty_bank_price:.2f}</div>
        <p class="{'green-text' if nifty_bank_change >= 0 else 'red-text'}" style="margin: 0;">
            {'+' if nifty_bank_change >= 0 else ''}{nifty_bank_change:.2f} ({nifty_bank_pct:.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="text-align: center; height: 100px;">
        <span class="metric-label">NIFTY IT</span>
        <div class="metric-value">{nifty_it_price:.2f}</div>
        <p class="{'green-text' if nifty_it_change >= 0 else 'red-text'}" style="margin: 0;">
            {'+' if nifty_it_change >= 0 else ''}{nifty_it_change:.2f} ({nifty_it_pct:.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

# Stock Market Basics for beginners expandable section
with st.expander("📚 Stock Market Basics for Beginners"):
    # Using separate components instead of a single large HTML string
    st.subheader("Understanding Stock Market Fundamentals")

    st.write(
        "The stock market is a platform where buyers and sellers trade shares of publicly listed companies. Understanding the basics can help you make informed investment decisions.")

    # Basic Terminology Section
    st.markdown("### Basic Terminology")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        - **Stock/Share:** A unit of ownership in a company
        - **BSE/NSE:** Bombay Stock Exchange and National Stock Exchange - India's primary exchanges
        - **Bull Market:** A market where prices are rising
        - **Bear Market:** A market where prices are falling
        - **Dividend:** A distribution of company profits to shareholders
        - **IPO:** Initial Public Offering - when a company first offers shares
        """)

    with col2:
        st.markdown("""
        - **Market Cap:** Total value of a company's outstanding shares
        - **P/E Ratio:** Price-to-Earnings ratio - measures valuation
        - **EPS:** Earnings Per Share - profit divided by outstanding shares
        - **52-Week Range:** Highest/lowest prices in past year
        - **Volume:** Number of shares traded in a period
        - **Beta:** Measures volatility compared to overall market
        """)

    # Chart Analysis Section
    st.markdown("### Chart Analysis")
    st.markdown("""
    - **Line Chart:** Shows closing prices over time as a continuous line
    - **Candlestick Chart:** Displays open, high, low, and close prices for each period
    - **Moving Averages:** Average price over a specific time period to identify trends
    - **Support/Resistance:** Price levels where stocks have difficulty moving above or below
    """)

    # Tips Section
    st.markdown("### Tips for Beginners")
    st.markdown("""
    1. **Start with established companies** that have stable business models and finances
    2. **Diversify your investments** across different sectors to manage risk
    3. **Focus on long-term investing** rather than short-term trading
    4. **Research thoroughly** before investing - understand the business fundamentals
    5. **Monitor corporate events** like earnings reports and industry developments
    6. **Reinvest dividends** to benefit from compound growth
    7. **Be patient** and avoid emotional decisions based on market fluctuations
    """)

    # Additional resources
    st.markdown("### Learning Resources")
    st.markdown("""
    - **Books:** "The Intelligent Investor" by Benjamin Graham
    - **Websites:** NSE India, BSE India, Investopedia
    - **Apps:** Zerodha Varsity, Groww Learn
    - **YouTube Channels:** Finance with Sharan, CA Rachana Ranade
    """)


# Function to get stock data
@st.cache_data(ttl=3600, show_spinner=False)
def load_stock_data(ticker, period='1y'):
    """
    Load stock data for the given ticker symbol

    Parameters:
    ticker (str): Stock ticker symbol
    period (str): Time period for historical data

    Returns:
    tuple: Stock information and historical data
    """
    try:
        # Get stock information
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get historical market data
        hist = stock.history(period=period)

        # Check if data was retrieved
        if hist.empty:
            return None, None

        return info, hist
    except Exception as e:
        st.error(f"Error retrieving data: {e}")
        return None, None


@st.cache_data(ttl=86400, show_spinner=False)
def search_stock_symbols(query):
    """
    Search for stock symbols and company names based on a query

    Parameters:
    query (str): Search query

    Returns:
    list: List of dictionaries containing stock symbols and company names
    """
    try:
        # Yahoo Finance API endpoint for symbol suggestions
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=20&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'quotes' in data and len(data['quotes']) > 0:
                results = []
                for quote in data['quotes']:
                    # Only include equities, not currencies, futures, etc.
                    if 'symbol' in quote and 'shortname' in quote and 'quoteType' in quote:
                        if quote['quoteType'] in ['EQUITY', 'ETF']:
                            results.append({
                                'symbol': quote['symbol'],
                                'name': quote['shortname'],
                                'exchange': quote.get('exchange', '')
                            })
                return results
        return []
    except Exception as e:
        # Silently fail and return empty list
        return []


# Function to get commonly used stock symbols (as a fallback)
@st.cache_data(ttl=86400, show_spinner=False)
def get_popular_stocks(query):
    """
    Get a list of popular stocks that match the query

    Parameters:
    query (str): Search query (prefix)

    Returns:
    list: List of dictionaries containing stock symbols and company names
    """
    # List of popular Indian stock symbols and names (NSE)
    popular_stocks = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd."},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd."},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd."},
        {"symbol": "INFY.NS", "name": "Infosys Ltd."},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd."},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Ltd."},
        {"symbol": "SBIN.NS", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd."},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd."},
        {"symbol": "ITC.NS", "name": "ITC Ltd."},
        {"symbol": "LT.NS", "name": "Larsen & Toubro Ltd."},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank Ltd."},
        {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Ltd."},
        {"symbol": "HCLTECH.NS", "name": "HCL Technologies Ltd."},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Ltd."},
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd."},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd."},
        {"symbol": "TITAN.NS", "name": "Titan Company Ltd."},
        {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd."},
        {"symbol": "WIPRO.NS", "name": "Wipro Ltd."},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Ltd."},
        {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Ltd."},
        {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corporation Ltd."},
        {"symbol": "NTPC.NS", "name": "NTPC Ltd."},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd."},
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel Ltd."},
        {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Ltd."},
        {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd."},
        {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance Company Ltd."},
        {"symbol": "COALINDIA.NS", "name": "Coal India Ltd."},
        {"symbol": "JSWSTEEL.NS", "name": "JSW Steel Ltd."},
        {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and Special Economic Zone Ltd."},
        {"symbol": "TECHM.NS", "name": "Tech Mahindra Ltd."},
        {"symbol": "NESTLEIND.NS", "name": "Nestle India Ltd."},
        {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank Ltd."},
        {"symbol": "NIFTY50.NS", "name": "Nifty 50 Index"},
        {"symbol": "BANKNIFTY.NS", "name": "Nifty Bank Index"}
    ]

    # Filter stocks based on query (case-insensitive)
    query = query.lower()
    filtered_stocks = []

    for stock in popular_stocks:
        if (stock["symbol"].lower().startswith(query) or
                query in stock["name"].lower() or
                stock["symbol"].lower() == query):
            filtered_stocks.append(stock)

    return filtered_stocks


# Function to create a downloadable CSV
def get_csv_download_link(df, filename="stock_data.csv"):
    """
    Generate a download link for a DataFrame as CSV

    Parameters:
    df (pandas.DataFrame): DataFrame to convert to CSV
    filename (str): Name of the file to download

    Returns:
    str: HTML download link
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href


# Function to format large numbers
def format_number(num):
    """Format large numbers to K, M, B, T format"""
    if num is None:
        return "N/A"

    if isinstance(num, str):
        return num

    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"


# Function to get news for a stock
@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_news(ticker, num_items=5):
    """
    Get latest news for a stock

    Parameters:
    ticker (str): Stock ticker symbol
    num_items (int): Number of news items to retrieve

    Returns:
    list: List of news items
    """
    try:
        # Get the ticker object
        stock = yf.Ticker(ticker)

        # Get news
        news = stock.news

        # Limit to specified number of items
        news = news[:num_items] if news and len(news) > 0 else []

        return news
    except Exception as e:
        # Silently fail
        return []


# Function to get market news (general)
@st.cache_data(ttl=3600, show_spinner=False)
def get_market_news(num_items=5):
    """
    Get general market news

    Parameters:
    num_items (int): Number of news items to retrieve

    Returns:
    list: List of news items
    """
    try:
        # Use either NIFTY50.NS or SENSEX.BO to get market news
        market = yf.Ticker("^NSEI")  # NIFTY 50 Index

        # Get news
        news = market.news

        # Limit to specified number of items
        news = news[:num_items] if news and len(news) > 0 else []

        return news
    except Exception as e:
        # Silently fail
        return []


# Function to get data for multiple stocks (watchlist)
@st.cache_data(ttl=900, show_spinner=False)  # Cache for 15 minutes
def get_watchlist_data(symbols):
    """
    Get current price data for multiple stocks

    Parameters:
    symbols (list): List of stock symbols

    Returns:
    list: List of dictionaries with stock data
    """
    results = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")

            if not hist.empty and 'Close' in hist.columns:
                current_price = hist['Close'].iloc[-1]
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                pct_change = (change / prev_close) * 100 if prev_close else 0

                results.append({
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'price': current_price,
                    'change': change,
                    'pct_change': pct_change,
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', 0)
                })
        except Exception as e:
            # Skip stocks with errors
            continue

    return results


# Function to get penny stocks data
@st.cache_data(ttl=86400, show_spinner=False)  # Cache for a day
def get_penny_stocks():
    """
    Get a curated list of penny stocks from India

    Returns:
    list: List of dictionaries with penny stock data
    """
    # List of promising Indian penny stocks (price < ₹100)
    # Updated with verified symbols that are available on Yahoo Finance
    penny_stocks = [
        {"symbol": "YESBANK.NS", "name": "Yes Bank Ltd.", "sector": "Banking",
         "desc": "Recovering private bank focusing on digital transformation"},
        {"symbol": "SUZLON.NS", "name": "Suzlon Energy Ltd.", "sector": "Renewable Energy",
         "desc": "Wind power equipment manufacturer with global presence"},
        {"symbol": "IDFC.NS", "name": "IDFC Ltd.", "sector": "Finance",
         "desc": "Infrastructure finance company with focus on banking and financial services"},
        {"symbol": "PNB.NS", "name": "Punjab National Bank", "sector": "Banking",
         "desc": "One of India's largest public sector banks with nationwide presence"},
        {"symbol": "ZOMATO.NS", "name": "Zomato Ltd.", "sector": "Technology",
         "desc": "Leading food delivery platform expanding into quick commerce"},
        {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "sector": "Banking",
         "desc": "Major public sector bank with international presence"},
        {"symbol": "FEDERALBNK.NS", "name": "Federal Bank Ltd.", "sector": "Banking",
         "desc": "Private sector bank with strong presence in South India"},
        {"symbol": "IRCTC.NS", "name": "Indian Railway Catering and Tourism Corp.", "sector": "Travel",
         "desc": "Railway ticketing and catering monopoly business"},
        {"symbol": "PETRONET.NS", "name": "Petronet LNG Ltd.", "sector": "Energy",
         "desc": "India's largest importer of liquefied natural gas"}
    ]

    # Get current data for these penny stocks
    results = []
    for stock in penny_stocks:
        try:
            # First check if we can get a history for this stock (validates the symbol)
            data = yf.Ticker(stock["symbol"])
            hist = data.history(period="1mo")

            if hist.empty or 'Close' not in hist.columns:
                continue

            # Get price data
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            price_30d_ago = hist['Close'].iloc[0] if len(hist) > 1 else current_price

            # Only process if we have valid price data
            if current_price and current_price > 0:
                # Calculate change
                pct_change_30d = ((
                                              current_price - price_30d_ago) / price_30d_ago) * 100 if price_30d_ago and price_30d_ago > 0 else 0

                # Get additional info if available
                info = data.info if hasattr(data, 'info') else {}

                results.append({
                    'symbol': stock["symbol"],
                    'name': stock["name"],
                    'sector': stock["sector"],
                    'description': stock["desc"],
                    'price': current_price,
                    'pct_change_30d': pct_change_30d
                })
        except Exception as e:
            # Skip stocks with errors but don't fail completely
            continue

    # If we couldn't get any valid data, return a default placeholder
    if not results:
        # Return at least two stocks we know exist (major Indian stocks)
        default_stocks = [
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd.", "sector": "Conglomerate",
             "desc": "India's largest private sector company with interests in petrochemicals, retail, and telecommunications"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd.", "sector": "IT Services",
             "desc": "India's largest IT services company with global operations"}
        ]

        # Try to get data for these default stocks
        for stock in default_stocks:
            try:
                data = yf.Ticker(stock["symbol"])
                hist = data.history(period="1mo")

                if not hist.empty and 'Close' in hist.columns:
                    current_price = hist['Close'].iloc[-1]
                    price_30d_ago = hist['Close'].iloc[0] if len(hist) > 1 else current_price
                    pct_change_30d = ((
                                                  current_price - price_30d_ago) / price_30d_ago) * 100 if price_30d_ago and price_30d_ago > 0 else 0

                    results.append({
                        'symbol': stock["symbol"],
                        'name': stock["name"],
                        'sector': stock["sector"],
                        'description': stock["desc"],
                        'price': current_price,
                        'pct_change_30d': pct_change_30d
                    })
            except:
                continue

    return results


# Input for stock symbol with search suggestions
col1, col2 = st.columns([3, 1])
with col1:
    # Initialize session state for stock symbol
    if 'stock_symbol' not in st.session_state:
        st.session_state.stock_symbol = "RELIANCE.NS"

    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []

    # Create a text input for the stock symbol
    search_query = st.text_input(
        "Enter Stock Symbol or Company Name",
        value=st.session_state.stock_symbol
    )

    # If the search query is at least 2 characters long, search for symbols
    if len(search_query) >= 2 and search_query != st.session_state.stock_symbol:
        with st.spinner("Searching..."):
            # First, try to get symbols from our local popular stocks list for quick results
            popular_results = get_popular_stocks(search_query)

            # Then get results from Yahoo Finance API
            api_results = search_stock_symbols(search_query)

            # Combine results (prioritize our popular stocks)
            combined_results = popular_results.copy()

            # Add API results that aren't duplicates
            existing_symbols = [stock['symbol'] for stock in combined_results]
            for result in api_results:
                if result['symbol'] not in existing_symbols:
                    combined_results.append(result)

            # Save the combined results
            st.session_state.search_results = combined_results

    # Display search results as buttons
    if st.session_state.search_results:
        st.write("**Suggested Stocks:**")
        cols = st.columns(2)
        for i, result in enumerate(st.session_state.search_results[:6]):  # Limit to 6 suggestions
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(f"{result['symbol']} - {result['name']}", key=f"suggestion_{i}"):
                    st.session_state.stock_symbol = result['symbol']
                    st.session_state.search_results = []
                    # Use rerun to update the page with the selected symbol
                    st.rerun()

    # Use the selected stock symbol (from session state or direct input)
    if search_query.upper() != st.session_state.stock_symbol and not st.session_state.search_results:
        # If user manually entered a symbol and no suggestions shown
        stock_symbol = search_query.upper()
        st.session_state.stock_symbol = stock_symbol
    else:
        stock_symbol = st.session_state.stock_symbol.upper()

with col2:
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }
    selected_period = st.selectbox("Select Time Period", list(period_options.keys()))
    period = period_options[selected_period]

# Add watchlist section
st.markdown('<div class="sub-header">👀 Your Watchlist</div>', unsafe_allow_html=True)


# Define functions for watchlist management
def add_to_watchlist(symbol):
    if symbol not in st.session_state.watchlist and symbol != "":
        st.session_state.watchlist.append(symbol)
        return True
    return False


def remove_from_watchlist(symbol):
    if symbol in st.session_state.watchlist:
        st.session_state.watchlist.remove(symbol)
        return True
    return False


# Create three columns - one for adding to watchlist, two for displaying the watchlist data
watchlist_col1, watchlist_col2 = st.columns([1, 3])

with watchlist_col1:
    # Add to watchlist section
    st.markdown("**Add to Watchlist**")
    new_symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS)", key="new_watchlist_item")

    if st.button("➕ Add to Watchlist", key="add_watchlist_btn"):
        if add_to_watchlist(new_symbol.upper()):
            st.success(f"Added {new_symbol.upper()} to watchlist!")
            time.sleep(1)
            st.rerun()
        else:
            if new_symbol == "":
                st.warning("Please enter a valid stock symbol")
            else:
                st.info(f"{new_symbol.upper()} is already in your watchlist")

with watchlist_col2:
    # Display watchlist data
    if st.session_state.watchlist:
        # Get data for all watchlist stocks
        with st.spinner("Loading watchlist data..."):
            watchlist_data = get_watchlist_data(st.session_state.watchlist)

        if watchlist_data:
            # Create a DataFrame for better display
            watchlist_df = pd.DataFrame(watchlist_data)


            # Format the display with colors for price changes
            def highlight_change(val):
                color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f'color: {color}'


            # Display in a clean table using the recommended style.map() method
            styled_df = watchlist_df[['symbol', 'name', 'price', 'pct_change']].rename(
                columns={
                    'symbol': 'Symbol',
                    'name': 'Company',
                    'price': 'Price (₹)',
                    'pct_change': 'Change (%)'
                }
            ).style.format({
                'Price (₹)': '{:.2f}',
                'Change (%)': '{:.2f}%'
            })

            # Apply color formatting to the Change column
            styled_df = styled_df.map(
                lambda val: f'color: {"green" if val > 0 else "red" if val < 0 else "black"}',
                subset=['Change (%)']
            )

            st.dataframe(styled_df)

            # Add remove buttons for each stock
            cols = st.columns(len(watchlist_data))
            for i, (col, stock) in enumerate(zip(cols, watchlist_data)):
                with col:
                    if st.button(f"🗑️ Remove {stock['symbol']}", key=f"remove_{i}"):
                        remove_from_watchlist(stock['symbol'])
                        st.rerun()
        else:
            st.info("Unable to fetch data for your watchlist. Please try again later.")
    else:
        st.info("Your watchlist is empty. Add stocks to track them here.")

# Penny Stocks Section with enhanced UI
st.markdown('<div class="sub-header">💰 Promising Penny Stocks</div>', unsafe_allow_html=True)

# Improved info box with better styling
st.markdown("""
<div class="info-box" style="background: linear-gradient(to right, #f8f9fa, #e9ecef); border-left: 5px solid #FF6B6B; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <h4 style="color: #FF6B6B; margin-top: 0;">What are Penny Stocks?</h4>
    <p style="margin-bottom: 10px;">Penny stocks are shares of small companies that trade at relatively low prices (usually under ₹100 in India). They offer potential for high returns but come with increased risk.</p>
    <div style="display: flex; gap: 20px; margin-top: 15px;">
        <div style="flex: 1;">
            <h5 style="color: #3D5A80; margin-top: 0;">Advantages ✅</h5>
            <ul style="padding-left: 20px; margin-top: 5px;">
                <li>Low entry price</li>
                <li>High growth potential</li>
                <li>Portfolio diversification</li>
            </ul>
        </div>
        <div style="flex: 1;">
            <h5 style="color: #3D5A80; margin-top: 0;">Risks ⚠️</h5>
            <ul style="padding-left: 20px; margin-top: 5px;">
                <li>Higher volatility</li>
                <li>Lower liquidity</li>
                <li>Limited company information</li>
            </ul>
        </div>
    </div>
    <p style="margin-top: 15px; font-style: italic; color: #555;">Always conduct thorough research before investing in penny stocks as they can be highly volatile.</p>
</div>
""", unsafe_allow_html=True)

# Add filter options with tabs
tab1, tab2, tab3 = st.tabs(["All Penny Stocks", "By Sector", "By Performance"])

# Get penny stocks data
with st.spinner("Loading penny stocks data..."):
    penny_stocks_data = get_penny_stocks()

if penny_stocks_data:
    # Sort stocks by price for consistent display
    penny_stocks_data = sorted(penny_stocks_data, key=lambda x: x['price'])

    with tab1:
        # Display in list view with detailed information
        st.markdown("""
        <style>
        .penny-stock-list {
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create a data table for all penny stocks
        data = []
        for stock in penny_stocks_data:
            change_arrow = "↑" if stock['pct_change_30d'] > 0 else "↓"

            # Create performance indicator without HTML formatting (for table display)
            performance = f"{change_arrow} {abs(stock['pct_change_30d']):.2f}%"

            data.append({
                "Symbol": stock['symbol'],
                "Name": stock['name'],
                "Sector": stock['sector'],
                "Price (₹)": f"₹{stock['price']:.2f}",
                "30-Day Change": performance,
                "Action": stock  # We'll use this for action buttons
            })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Format the dataframe for display
        formatted_df = df.copy()
        formatted_df = formatted_df.drop(columns=["Action"])

        # Display as table
        st.markdown("<h4>Complete Penny Stock List</h4>", unsafe_allow_html=True)
        st.write("Click on any row to see more details about that stock")


        # Style the dataframe to colorize the 30-Day Change column
        def style_change_column(df):
            styled = df.copy()
            # Apply styling to the 30-Day Change column
            for i, row in styled.iterrows():
                change_text = row['30-Day Change']
                if "↑" in change_text:
                    styled.loc[
                        i, '30-Day Change'] = f"<span style='color: #26A69A; font-weight: bold;'>{change_text}</span>"
                else:
                    styled.loc[
                        i, '30-Day Change'] = f"<span style='color: #EF5350; font-weight: bold;'>{change_text}</span>"
            return styled


        # Apply styling and convert to HTML
        styled_html = style_change_column(formatted_df).to_html(escape=False, index=False)

        # Display using st.dataframe (for interaction) and st.markdown (for styling)
        st.dataframe(
            formatted_df,
            hide_index=True,
            use_container_width=True
        )

        # Add note about sorting
        st.info("💡 Tip: Click on any column header to sort the table by that column")

        # Display detailed list below the table
        st.markdown("### Detailed Stock Information", unsafe_allow_html=True)

        # Sort by name for consistent display
        sorted_stocks = sorted(penny_stocks_data, key=lambda x: x['name'])

        for i, stock in enumerate(sorted_stocks):
            change_color = "#26A69A" if stock['pct_change_30d'] > 0 else "#EF5350"
            change_arrow = "↑" if stock['pct_change_30d'] > 0 else "↓"

            # Calculate performance bars
            performance_bars = ""
            perf_val = min(max(int(abs(stock['pct_change_30d']) / 5), 1), 5)
            if stock['pct_change_30d'] > 0:
                performance_bars = "🟢" * perf_val
            else:
                performance_bars = "🔴" * perf_val

            # Create an expandable section for each stock
            with st.expander(f"{stock['name']} ({stock['symbol']})"):
                # Create two columns for layout
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Sector:** {stock['sector']}")
                    st.markdown(f"**Price:** ₹{stock['price']:.2f}")
                    st.markdown(f"""**30-Day Performance:** 
                    <span style='color: {change_color}; font-weight: bold;'>
                        {change_arrow} {abs(stock['pct_change_30d']):.2f}% {performance_bars}
                    </span>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**Description:** {stock['description']}")

                with col2:
                    # Add action buttons
                    if st.button(f"📊 Analyze", key=f"analyze_detail_{i}"):
                        st.session_state.stock_symbol = stock['symbol']
                        st.rerun()

                    if stock['symbol'] in st.session_state.watchlist:
                        if st.button(f"❌ Remove from Watchlist", key=f"remove_watchlist_detail_{i}"):
                            st.session_state.watchlist.remove(stock['symbol'])
                            st.success(f"Removed {stock['symbol']} from watchlist!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        if st.button(f"➕ Add to Watchlist", key=f"add_watchlist_detail_{i}"):
                            if stock['symbol'] not in st.session_state.watchlist:
                                st.session_state.watchlist.append(stock['symbol'])
                                st.success(f"Added {stock['symbol']} to watchlist!")
                                time.sleep(1)
                                st.rerun()

                # Add a horizontal separator
                st.markdown("---")

    with tab2:
        # Group stocks by sector
        sectors = {}
        for stock in penny_stocks_data:
            sector = stock['sector']
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(stock)

        # Display stocks by sector
        for sector, stocks in sectors.items():
            st.subheader(f"📌 {sector}")

            # Create table view for this sector
            data = []
            for stock in stocks:
                change_arrow = "↑" if stock['pct_change_30d'] > 0 else "↓"
                data.append({
                    "Symbol": stock['symbol'],
                    "Name": stock['name'],
                    "Price (₹)": f"₹{stock['price']:.2f}",
                    "30-Day Change": f"{change_arrow} {abs(stock['pct_change_30d']):.2f}%",
                    "Action": stock['symbol']  # We'll use this for action buttons
                })

            # Convert to DataFrame
            if data:
                df = pd.DataFrame(data)

                # Display styled dataframe without ButtonColumn which may not be available in this Streamlit version
                st.dataframe(
                    df.drop(columns=["Action"]),  # Remove the Action column as we'll add buttons below
                    hide_index=True,
                    width=800
                )

                # Add action buttons below the table instead
                cols = st.columns(len(stocks))
                for i, stock in enumerate(stocks):
                    with cols[i]:
                        if st.button(f"📊 Analyze {stock['symbol']}", key=f"analyze_sector_{sector}_{i}"):
                            st.session_state.stock_symbol = stock['symbol']
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

    with tab3:
        # Sort by performance
        gainers = sorted([s for s in penny_stocks_data if s['pct_change_30d'] > 0],
                         key=lambda x: x['pct_change_30d'], reverse=True)
        losers = sorted([s for s in penny_stocks_data if s['pct_change_30d'] <= 0],
                        key=lambda x: x['pct_change_30d'])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🟢 Top Gainers (30d)")
            if gainers:
                # Create styled table for gainers
                for stock in gainers:
                    st.markdown(f"""
                    <div style="border-left: 4px solid #26A69A; padding: 10px; margin-bottom: 10px; background-color: rgba(38, 166, 154, 0.1); border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: bold;">{stock['symbol']}</span>
                            <span style="color: #26A69A; font-weight: bold;">↑ {stock['pct_change_30d']:.2f}%</span>
                        </div>
                        <div>{stock['name']}</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">₹{stock['price']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No gainers in the selected period")

        with col2:
            st.subheader("🔴 Top Losers (30d)")
            if losers:
                # Create styled table for losers
                for stock in losers:
                    st.markdown(f"""
                    <div style="border-left: 4px solid #EF5350; padding: 10px; margin-bottom: 10px; background-color: rgba(239, 83, 80, 0.1); border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: bold;">{stock['symbol']}</span>
                            <span style="color: #EF5350; font-weight: bold;">↓ {abs(stock['pct_change_30d']):.2f}%</span>
                        </div>
                        <div>{stock['name']}</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">₹{stock['price']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No losers in the selected period")

    # Add a disclaimer at the bottom
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 20px; font-size: 0.9rem; color: #666;">
        <strong>Disclaimer:</strong> The information provided is for educational purposes only and should not be considered as investment advice. 
        Past performance is not indicative of future results. Please consult a financial advisor before making investment decisions.
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("Unable to load penny stocks data. Please try again later.")

# Button to get data in a colorful style
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF4F4F;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

if st.button("📊 Analyze Stock Data"):
    # Display loading state
    with st.spinner(f"Loading data for {stock_symbol}..."):
        # Get stock data
        info, hist = load_stock_data(stock_symbol, period)

        if info is None or hist is None:
            st.error(f"Unable to fetch data for {stock_symbol}. Please check the symbol and try again.")
        else:
            # Create two columns layout
            col1, col2 = st.columns([1, 1])

            # Column 1: Company Information with card styling
            with col1:
                st.markdown('<div class="sub-header">🏢 Company Profile</div>', unsafe_allow_html=True)

                # Format company name and sector
                company_name = info.get('longName', 'N/A')
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                website = info.get('website', '#')

                # Display company info in a stylized card
                st.markdown(f"""
                <div class="card">
                    <h3 style="color: #FF6B6B; margin-top: 0;">{company_name}</h3>
                    <p><strong>Symbol:</strong> {stock_symbol}</p>
                    <p><strong>Sector:</strong> {sector}</p>
                    <p><strong>Industry:</strong> {industry}</p>
                    <p><strong>Exchange:</strong> {info.get('exchange', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Get current price and calculate daily change
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                prev_close = info.get('previousClose', 0)

                if current_price and prev_close:
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100 if prev_close else 0

                    # Color based on price movement
                    color_class = "green-text" if change >= 0 else "red-text"
                    arrow = "↑" if change >= 0 else "↓"

                    # Display current price with change info
                    st.markdown(f"""
                    <div class="card" style="text-align: center;">
                        <h2 style="margin: 0; color: #3D5A80;">₹{current_price:.2f}</h2>
                        <p class="{color_class}" style="font-size: 1.2rem; margin: 5px 0;">
                            {arrow} ₹{abs(change):.2f} ({abs(change_pct):.2f}%)
                        </p>
                        <p>Last Trading Day</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Create key metrics in a grid layout
                st.markdown('<div class="sub-header">📊 Key Metrics</div>', unsafe_allow_html=True)

                # Create 2x2 grid for important metrics
                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.markdown(f"""
                    <div class="card" style="text-align: center; height: 90px;">
                        <span class="metric-label">Market Cap</span>
                        <div class="metric-value">{format_number(info.get('marketCap', 'N/A'))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="card" style="text-align: center; height: 90px;">
                        <span class="metric-label">52W High</span>
                        <div class="metric-value">₹{info.get('fiftyTwoWeekHigh', 'N/A')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with metric_col2:
                    st.markdown(f"""
                    <div class="card" style="text-align: center; height: 90px;">
                        <span class="metric-label">P/E Ratio</span>
                        <div class="metric-value">{info.get('trailingPE', 'N/A')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="card" style="text-align: center; height: 90px;">
                        <span class="metric-label">52W Low</span>
                        <div class="metric-value">₹{info.get('fiftyTwoWeekLow', 'N/A')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # More metrics in expandable section
                with st.expander("View All Metrics"):
                    # Create metrics dataframe
                    metrics_data = {
                        'Metric': [
                            'Current Price',
                            'Previous Close',
                            'Open',
                            'Day High',
                            'Day Low',
                            'Volume',
                            'Market Cap',
                            'PE Ratio',
                            'Dividend Yield',
                            '52 Week High',
                            '52 Week Low',
                            'EPS',
                            'Beta'
                        ],
                        'Value': [
                            f"₹{info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}",
                            f"₹{info.get('previousClose', 'N/A')}",
                            f"₹{info.get('open', info.get('regularMarketOpen', 'N/A'))}",
                            f"₹{info.get('dayHigh', info.get('regularMarketDayHigh', 'N/A'))}",
                            f"₹{info.get('dayLow', info.get('regularMarketDayLow', 'N/A'))}",
                            format_number(info.get('volume', info.get('regularMarketVolume', 'N/A'))),
                            format_number(info.get('marketCap', 'N/A')),
                            f"{info.get('trailingPE', 'N/A')}",
                            f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A",
                            f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}",
                            f"₹{info.get('fiftyTwoWeekLow', 'N/A')}",
                            f"₹{info.get('trailingEps', 'N/A')}",
                            f"{info.get('beta', 'N/A')}"
                        ]
                    }

                    metrics_df = pd.DataFrame(metrics_data)
                    st.table(metrics_df)

                    # Download link for company metrics
                    st.markdown(f"""
                    <a href="data:file/csv;base64,{base64.b64encode(metrics_df.to_csv(index=False).encode()).decode()}" 
                    download="{stock_symbol}_metrics.csv" class="download-btn">
                    📥 Download Metrics
                    </a>
                    """, unsafe_allow_html=True)

            # Column 2: Stock Price Chart
            with col2:
                st.markdown('<div class="sub-header">📊 Price Chart</div>', unsafe_allow_html=True)

                # Chart type selector
                chart_type = st.radio(
                    "Select Chart Type",
                    ["Line Chart", "Candlestick Chart"],
                    horizontal=True
                )

                # Prepare data for plotting
                fig = go.Figure()

                if chart_type == "Line Chart":
                    # Calculate moving averages
                    hist['MA5'] = hist['Close'].rolling(window=5).mean()
                    hist['MA20'] = hist['Close'].rolling(window=20).mean()

                    # Add price line with gradient fill
                    fig.add_trace(
                        go.Scatter(
                            x=hist.index,
                            y=hist['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='#FF6B6B', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(255, 107, 107, 0.1)'
                        )
                    )

                    # Add moving averages
                    fig.add_trace(
                        go.Scatter(
                            x=hist.index,
                            y=hist['MA5'],
                            mode='lines',
                            name='5-Day MA',
                            line=dict(color='#4ECDC4', width=1.5, dash='dot')
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=hist.index,
                            y=hist['MA20'],
                            mode='lines',
                            name='20-Day MA',
                            line=dict(color='#FFE66D', width=1.5, dash='dash')
                        )
                    )

                else:  # Candlestick Chart
                    # Add candlestick chart
                    fig.add_trace(
                        go.Candlestick(
                            x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close'],
                            name='Price',
                            increasing=dict(line=dict(color='#26A69A'), fillcolor='#26A69A'),
                            decreasing=dict(line=dict(color='#EF5350'), fillcolor='#EF5350')
                        )
                    )

                # Add volume bars
                colors = ['#26A69A' if row['Close'] >= row['Open'] else '#EF5350' for _, row in hist.iterrows()]

                fig.add_trace(
                    go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name='Volume',
                        yaxis='y2',
                        marker=dict(color=colors, opacity=0.5)
                    )
                )

                # Customize layout with better styling
                fig.update_layout(
                    title=f"{company_name} ({stock_symbol}) • {selected_period}",
                    xaxis_title="Date",
                    yaxis_title="Price (₹ INR)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis2=dict(
                        title="Volume",
                        overlaying="y",
                        side="right",
                        showgrid=False
                    ),
                    height=500,
                    template="plotly_white",
                    margin=dict(l=10, r=10, t=40, b=10)
                )

                # Show figure
                st.plotly_chart(fig, use_container_width=True)

            # Historical Data Table with better styling
            st.markdown('<div class="sub-header">📅 Historical Price Data</div>', unsafe_allow_html=True)

            # Format historical dataframe for display
            display_hist = hist.reset_index()
            display_hist['Date'] = display_hist['Date'].dt.date

            # Add price change and percentage columns
            display_hist['Change'] = display_hist['Close'] - display_hist['Open']
            display_hist['Change %'] = (display_hist['Change'] / display_hist['Open'] * 100)

            # Round all numeric columns to 2 decimal places
            display_hist = display_hist.round(2)

            # Style the dataframe using the modern style.map() method
            styled_df = display_hist.style

            # Apply color formatting to the Change columns
            styled_df = styled_df.map(
                lambda val: f'color: {"#26A69A" if val > 0 else "#EF5350" if val < 0 else "black"}; font-weight: bold',
                subset=['Change', 'Change %']
            )

            # Display the data with a height limit
            st.dataframe(styled_df, height=300, use_container_width=True)

            # Create an expander for download options
            with st.expander("Download Historical Data"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <a href="data:file/csv;base64,{base64.b64encode(display_hist.to_csv(index=False).encode()).decode()}" 
                    download="{stock_symbol}_historical_data.csv" class="download-btn">
                    📥 Download as CSV
                    </a>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <a href="data:file/excel;base64,{base64.b64encode(display_hist.to_excel(index=False).encode()).decode()}" 
                    download="{stock_symbol}_historical_data.xlsx" class="download-btn" style="background-color: #28a745;">
                    📊 Download as Excel
                    </a>
                    """, unsafe_allow_html=True)

            # Additional Information in a styled card
            st.markdown('<div class="sub-header">📝 About the Company</div>', unsafe_allow_html=True)

            business_summary = info.get('longBusinessSummary', "No business summary available.")

            st.markdown(f"""
            <div class="card" style="background-color: #f8f9fa;">
                <p style="text-align: justify; line-height: 1.6;">{business_summary}</p>

                <div style="margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px;">
                    <p><strong>Country:</strong> {info.get('country', 'India')}</p>
                    <p><strong>Currency:</strong> {info.get('currency', 'INR')} (Indian Rupee)</p>
                    <p><strong>Employees:</strong> {format_number(info.get('fullTimeEmployees', 'N/A'))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Get and display news related to the stock
            st.markdown('<div class="sub-header">📰 Latest News</div>', unsafe_allow_html=True)

            # Get company-specific news
            stock_news = get_stock_news(stock_symbol, num_items=3)

            if stock_news:
                # Display company-specific news
                st.markdown(f"""
                <div class="card">
                    <h4 style="color: #3D5A80; margin-top: 0;">Company News: {company_name}</h4>
                </div>
                """, unsafe_allow_html=True)

                # Display each news item in a card
                for item in stock_news:
                    # Format the date
                    publish_date = datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                    title = item.get('title', 'No title available')
                    summary = item.get('summary', 'No summary available')
                    url = item.get('link', '#')
                    source = item.get('publisher', 'Unknown Source')

                    # Display news in a styled card
                    st.markdown(f"""
                    <div class="card" style="margin-bottom: 10px; background-color: #f8f9fa;">
                        <h4 style="margin-top: 0;">{title}</h4>
                        <p style="color: #666; font-size: 0.8rem;">{publish_date} | Source: {source}</p>
                        <p>{summary[:200]}{'...' if len(summary) > 200 else ''}</p>
                        <a href="{url}" target="_blank" style="color: #FF6B6B; text-decoration: none; font-weight: bold;">
                            Read full article →
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            # Get general market news when company news is limited
            if len(stock_news) < 2:
                # Get market news
                market_news = get_market_news(num_items=3)

                if market_news:
                    st.markdown(f"""
                    <div class="card" style="margin-top: 20px;">
                        <h4 style="color: #3D5A80; margin-top: 0;">Market News: Indian Stock Market</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display each news item
                    for item in market_news:
                        # Format the date
                        publish_date = datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime(
                            '%Y-%m-%d %H:%M')
                        title = item.get('title', 'No title available')
                        summary = item.get('summary', 'No summary available')
                        url = item.get('link', '#')
                        source = item.get('publisher', 'Unknown Source')

                        # Display news in a styled card
                        st.markdown(f"""
                        <div class="card" style="margin-bottom: 10px; background-color: #f8f9fa;">
                            <h4 style="margin-top: 0;">{title}</h4>
                            <p style="color: #666; font-size: 0.8rem;">{publish_date} | Source: {source}</p>
                            <p>{summary[:200]}{'...' if len(summary) > 200 else ''}</p>
                            <a href="{url}" target="_blank" style="color: #FF6B6B; text-decoration: none; font-weight: bold;">
                                Read full article →
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

# Footer with a more colorful design
st.markdown("---")
st.markdown('<div class="footer">', unsafe_allow_html=True)

# Creating a 3-column layout for the footer
foot_col1, foot_col2, foot_col3 = st.columns(3)

with foot_col1:
    st.markdown('<h3 style="color: #FF6B6B;">📈 About</h3>', unsafe_allow_html=True)
    st.markdown("Data provided by Yahoo Finance API using the yfinance library.")
    st.markdown("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with foot_col2:
    st.markdown('<h3 style="color: #FF6B6B;">🇮🇳 Stock Exchanges</h3>', unsafe_allow_html=True)
    st.markdown("""
    <ul>
        <li><b>NSE:</b> Use <span class="highlight">.NS</span> suffix (e.g., RELIANCE.NS)</li>
        <li><b>BSE:</b> Use <span class="highlight">.BO</span> suffix (e.g., RELIANCE.BO)</li>
    </ul>
    """, unsafe_allow_html=True)

with foot_col3:
    st.markdown('<h3 style="color: #FF6B6B;">⏰ Trading Hours</h3>', unsafe_allow_html=True)
    st.markdown("""
    <ul>
        <li>Monday to Friday</li>
        <li>9:15 AM to 3:30 PM IST (UTC+5:30)</li>
        <li>Closed on market holidays</li>
    </ul>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add credit line with heart emoji and developer name
st.markdown("""
<div style="text-align: center; margin-top: 20px; margin-bottom: 10px; font-size: 0.9rem;">
    Made with ❤️ in India by <b>Sridhar</b> - Powered by <span style="color: #FF6B6B; font-weight: bold;">GlobalDevForce</span>
</div>
""", unsafe_allow_html=True)

# Add a colorful separator at the very bottom
st.markdown("""
<div style="width: 100%; height: 5px; background: linear-gradient(to right, #FF6B6B, #4ECDC4, #FFE66D, #FF6B6B);"></div>
""", unsafe_allow_html=True)
