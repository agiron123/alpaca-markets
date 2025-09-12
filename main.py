from alpaca.data.live import CryptoDataStream, OptionDataStream, StockDataStream

# keys are required for live data
from dotenv import load_dotenv
import os

from alpaca.data.models.quotes import Quote
from alpaca.data.models.trades import Trade
from alpaca.data.models.bars import Bar
from alpaca.data.models.orderbooks import Orderbook

# First, load the .env file
load_dotenv()

crypto_stream = CryptoDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)

async def crypto_stream_trades_handler(message):
    print("TradeStream: ", message)
    
async def crypto_stream_quotes_handler(message):
    print("QuoteStream: ", message)
    
async def crypto_stream_minute_bars_handler(message):
    print("MinuteBarStream: ", message)
    
async def crypto_stream_daily_bars_handler(message):
    print("DailyBarStream: ", message)

async def crypto_stream_orderbooks_handler(message):
    print("OrderbookStream: ", message)


def main():
    print("Hello from alpaca-markets!")
    # Subscribe to the trades as they come through for all symbols
    crypto_stream.subscribe_trades(crypto_stream_trades_handler, "BTC/USD", "ETH/USD")

    # Subscribe to the quotes as they come through for all symbols
    crypto_stream.subscribe_quotes(crypto_stream_quotes_handler, "BTC/USD", "ETH/USD")

    # Subscribe to bar streams as they come through
    crypto_stream.subscribe_bars(crypto_stream_minute_bars_handler, "BTC/USD", "ETH/USD")
    crypto_stream.subscribe_daily_bars(crypto_stream_daily_bars_handler, "BTC/USD", "ETH/USD")

    # Subscribe to orderbook streams as they come through
    crypto_stream.subscribe_orderbooks(crypto_stream_orderbooks_handler, "BTC/USD", "ETH/USD")

    crypto_stream.run()

if __name__ == "__main__":
    main()
