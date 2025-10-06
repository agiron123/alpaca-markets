# Alpaca Markets Crypto Data Streaming

A Python application for streaming real-time cryptocurrency data from Alpaca Markets API. This project demonstrates how to subscribe to and handle live crypto market data including trades, quotes, bars, and orderbooks.

## Features

- Real-time cryptocurrency trade streaming
- Live quote data for crypto pairs
- Minute and daily bar data streaming
- Orderbook data streaming
- Support for multiple crypto pairs (BTC/USD, ETH/USD)

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

Run the main script to start streaming crypto data:

```bash
python main.py
```

The application will subscribe to various data streams for BTC/USD and ETH/USD and print the data as it arrives.

## Project Structure

- `main.py` - Main application entry point with stream handlers
- `pyproject.toml` - Project dependencies and configuration
- `.env` - API credentials (not tracked in git)

## Dependencies

- `alpaca-py` - Official Alpaca Markets Python SDK
- `python-dotenv` - Environment variable management

## License

This project is for educational and development purposes.
