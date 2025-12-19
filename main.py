from alpaca.data.live import CryptoDataStream

# keys are required for live data
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# First, load the .env file
load_dotenv()
logger.debug("Environment variables loaded")

crypto_stream = CryptoDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)
logger.info("CryptoDataStream initialized")

async def crypto_stream_trades_handler(message):
    logger.debug(f"TradeStream: {message}")
    
async def crypto_stream_quotes_handler(message):
    logger.debug(f"QuoteStream: {message}")
    
async def crypto_stream_minute_bars_handler(message):
    logger.debug(f"MinuteBarStream: {message}")
    
async def crypto_stream_daily_bars_handler(message):
    logger.debug(f"DailyBarStream: {message}")

async def crypto_stream_orderbooks_handler(message):
    logger.debug(f"OrderbookStream: {message}")


def main():
    logger.info("Starting alpaca-markets crypto data stream")
    try:
        # Subscribe to the trades as they come through for all symbols
        crypto_stream.subscribe_trades(crypto_stream_trades_handler, "BTC/USD", "ETH/USD")
        logger.info("Subscribed to trades for BTC/USD, ETH/USD")

        # Subscribe to the quotes as they come through for all symbols
        crypto_stream.subscribe_quotes(crypto_stream_quotes_handler, "BTC/USD", "ETH/USD")
        logger.info("Subscribed to quotes for BTC/USD, ETH/USD")

        # Subscribe to bar streams as they come through
        crypto_stream.subscribe_bars(crypto_stream_minute_bars_handler, "BTC/USD", "ETH/USD")
        logger.info("Subscribed to minute bars for BTC/USD, ETH/USD")
        crypto_stream.subscribe_daily_bars(crypto_stream_daily_bars_handler, "BTC/USD", "ETH/USD")
        logger.info("Subscribed to daily bars for BTC/USD, ETH/USD")

        # Subscribe to orderbook streams as they come through
        crypto_stream.subscribe_orderbooks(crypto_stream_orderbooks_handler, "BTC/USD", "ETH/USD")
        logger.info("Subscribed to orderbooks for BTC/USD, ETH/USD")

        logger.info("Starting crypto data stream event loop")
        crypto_stream.run()
    except Exception as e:
        logger.error(f"Error in crypto stream: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
