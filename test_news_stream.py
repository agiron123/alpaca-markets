#!/usr/bin/env python3
"""
Test script to verify that news streaming is configured correctly.
This script will attempt to connect to the Alpaca News stream and wait for a single news article.
"""

from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.debug("Environment variables loaded")

# Initialize the news data stream
news_stream = NewsDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)
logger.info("NewsDataStream initialized for testing")

# Counter for received news
news_count = 0
MAX_NEWS = 3  # Stop after receiving 3 news articles


async def test_news_handler(news: News):
    """Test handler that prints basic news info and stops after MAX_NEWS articles."""
    global news_count
    news_count += 1
    
    logger.info(f"\n✅ News Article #{news_count} Received:")
    logger.info(f"   Headline: {news.headline}")
    logger.info(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    logger.info(f"   Source: {news.source}")
    logger.info(f"   Created: {news.created_at}")
    logger.debug(f"Test handler received news ID={news.id}, count={news_count}/{MAX_NEWS}")
    
    if news_count >= MAX_NEWS:
        logger.info(f"\n🎉 Successfully received {MAX_NEWS} news articles!")
        logger.info("✅ News streaming is working correctly!")
        logger.info("\nStopping stream...")
        logger.debug(f"Test complete: received {news_count} articles, stopping stream")
        # Stop the stream
        await news_stream.stop_ws()


def main():
    """Main test function."""
    logger.info("=" * 80)
    logger.info("Testing Alpaca News Data Stream Connection")
    logger.info("=" * 80)
    
    api_key = os.getenv('ALPACA_API_KEY')
    if api_key:
        logger.info(f"\n🔑 API Key: {api_key[:10]}...")
        logger.debug(f"API key length: {len(api_key)} characters")
    else:
        logger.error("API key not found in environment variables")
    
    test_symbols = ["AAPL", "TSLA", "MSFT"]
    logger.info(f"📊 Subscribing to news for: {', '.join(test_symbols)}")
    logger.info(f"⏱️  Waiting for {MAX_NEWS} news articles (this may take a while)...")
    logger.info("-" * 80)
    logger.debug(f"Test configuration: MAX_NEWS={MAX_NEWS}, symbols={test_symbols}")
    
    try:
        # Subscribe to a few popular symbols
        news_stream.subscribe_news(test_news_handler, *test_symbols)
        logger.info(f"Successfully subscribed to news for {len(test_symbols)} symbols")
        logger.debug("Starting test stream...")
        
        # Start the stream
        logger.info("Starting news data stream event loop for testing")
        news_stream.run()
        
        logger.info("Test completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Test interrupted by user")
        logger.info(f"Test received {news_count}/{MAX_NEWS} articles before interruption")
        return 1
    except Exception as e:
        logger.error(f"\n\n❌ Error occurred: {e}", exc_info=True)
        logger.error("\nTroubleshooting:")
        logger.error("1. Check that your API credentials in .env are correct")
        logger.error("2. Ensure you have an active Alpaca account with market data access")
        logger.error("3. Verify your internet connection")
        return 1


if __name__ == "__main__":
    exit(main())
