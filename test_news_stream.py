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

# Load environment variables
load_dotenv()

# Initialize the news data stream
news_stream = NewsDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)

# Counter for received news
news_count = 0
MAX_NEWS = 3  # Stop after receiving 3 news articles


async def test_news_handler(news: News):
    """Test handler that prints basic news info and stops after MAX_NEWS articles."""
    global news_count
    news_count += 1
    
    print(f"\n✅ News Article #{news_count} Received:")
    print(f"   Headline: {news.headline}")
    print(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    print(f"   Source: {news.source}")
    print(f"   Created: {news.created_at}")
    
    if news_count >= MAX_NEWS:
        print(f"\n🎉 Successfully received {MAX_NEWS} news articles!")
        print("✅ News streaming is working correctly!")
        print("\nStopping stream...")
        # Stop the stream
        await news_stream.stop_ws()


def main():
    """Main test function."""
    print("=" * 80)
    print("Testing Alpaca News Data Stream Connection")
    print("=" * 80)
    print(f"\n🔑 API Key: {os.getenv('ALPACA_API_KEY')[:10]}...")
    print(f"📊 Subscribing to news for: AAPL, TSLA, MSFT")
    print(f"⏱️  Waiting for {MAX_NEWS} news articles (this may take a while)...")
    print("-" * 80)
    
    try:
        # Subscribe to a few popular symbols
        news_stream.subscribe_news(test_news_handler, "AAPL", "TSLA", "MSFT")
        
        # Start the stream
        news_stream.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. Check that your API credentials in .env are correct")
        print("2. Ensure you have an active Alpaca account with market data access")
        print("3. Verify your internet connection")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
