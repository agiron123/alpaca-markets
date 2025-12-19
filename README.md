# Alpaca Markets Data Streaming

A Python application for streaming real-time market data from Alpaca Markets API. This project demonstrates how to subscribe to and handle live crypto market data and news feeds including trades, quotes, bars, orderbooks, and news articles.

## Features

### Cryptocurrency Data Streaming
- Real-time cryptocurrency trade streaming
- Live quote data for crypto pairs
- Minute and daily bar data streaming
- Orderbook data streaming
- Support for multiple crypto pairs (BTC/USD, ETH/USD)

### News Data Streaming
- Real-time news article streaming
- Support for symbol-specific or global news
- Advanced filtering by keywords, sources, and symbols
- JSON export functionality
- Rich formatted console output with emojis

## Requirements

- Python 3.11 or higher
- Alpaca Markets API credentials

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd alpaca-markets
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file in the project root with your Alpaca API credentials:
```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

## Usage

### Cryptocurrency Data Stream

Run the main script to start streaming crypto data:

```bash
python main.py
```

The application will subscribe to various data streams for BTC/USD and ETH/USD and print the data as it arrives.

### News Data Streams

We provide three different news streaming implementations:

#### 1. Basic News Stream (`news_stream.py`)

Simple news streaming for specific symbols with formatted output:

```bash
python news_stream.py
```

Subscribes to news for: AAPL, TSLA, MSFT, GOOGL, AMZN

#### 2. Advanced News Stream (`news_stream_advanced.py`)

Enhanced news streaming with JSON logging and detailed output:

```bash
python news_stream_advanced.py
```

Features:
- Streams news for 8 major tech stocks (AAPL, TSLA, MSFT, GOOGL, AMZN, NVDA, META, NFLX)
- Saves all news articles to `news_feed.jsonl` file
- Rich formatted console output with timestamps and emojis
- Displays article content and images

#### 3. Filtered News Stream (`news_stream_filtered.py`)

News streaming with advanced filtering capabilities:

```bash
python news_stream_filtered.py
```

Features:
- Subscribe to all symbols using wildcard (`*`)
- Filter by keywords (earnings, revenue, profit, acquisition, merger, SEC, FDA)
- Filter by minimum number of symbols mentioned
- Filter by news sources (optional)
- Keyword highlighting in output
- Saves filtered news to `filtered_news.jsonl`

You can customize the filters by editing the configuration variables at the top of the file:
- `SYMBOLS_TO_WATCH`: List of symbols or `["*"]` for all
- `FILTER_KEYWORDS`: List of keywords to filter by
- `MIN_SYMBOLS_COUNT`: Minimum number of symbols in news
- `FILTER_SOURCES`: List of preferred news sources

### Testing and Examples

#### Test News Stream (`test_news_stream.py`)

Quick test to verify your news streaming setup is working:

```bash
python test_news_stream.py
```

This script will connect to Alpaca's news stream and wait for 3 news articles to confirm everything is working correctly.

#### News Examples (`news_examples.py`)

Comprehensive examples demonstrating various news streaming patterns:

```bash
python news_examples.py
```

This file includes 5 different example patterns:
1. Basic news handler with simple output
2. Detailed news handler showing all available data
3. Filtered handler that only shows news matching specific keywords
4. Statistics tracker that counts news by source and symbol
5. Multiple handlers for different symbols

You can uncomment different examples in the `main()` function to try each one.

## Project Structure

- `main.py` - Cryptocurrency data streaming application
- `news_stream.py` - Basic news streaming for specific symbols
- `news_stream_advanced.py` - Advanced news streaming with logging
- `news_stream_filtered.py` - News streaming with filtering capabilities
- `news_examples.py` - Collection of example news streaming patterns
- `test_news_stream.py` - Test script to verify news streaming setup
- `pyproject.toml` - Project dependencies and configuration
- `.env` - API credentials (not tracked in git)
- `news_feed.jsonl` - Output file for advanced news stream (generated)
- `filtered_news.jsonl` - Output file for filtered news stream (generated)

## Dependencies

- `alpaca-py` - Official Alpaca Markets Python SDK
- `python-dotenv` - Environment variable management

## License

This project is for educational and development purposes.
