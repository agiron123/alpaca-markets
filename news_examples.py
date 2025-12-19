"""
Alpaca News Streaming Examples
================================

This file contains various examples of how to use the Alpaca News Data Stream API.
You can run the specific example you want by uncommenting it in the main() function.
"""

from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
from datetime import datetime
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


# ============================================================================
# Example 1: Basic News Handler
# ============================================================================

async def basic_news_handler(news: News):
    """Simple handler that prints headline and symbols."""
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] {news.headline}")
    logger.info(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    logger.debug(f"Basic handler processed news ID={news.id}")
    logger.info("")


# ============================================================================
# Example 2: Detailed News Handler
# ============================================================================

async def detailed_news_handler(news: News):
    """Handler that displays all available news data."""
    logger.info("=" * 80)
    logger.info(f"ID: {news.id}")
    logger.info(f"Headline: {news.headline}")
    logger.info(f"Author: {news.author}")
    logger.info(f"Created: {news.created_at}")
    logger.info(f"Updated: {news.updated_at}")
    logger.info(f"Symbols: {news.symbols}")
    logger.info(f"Source: {news.source}")
    logger.info(f"URL: {news.url}")
    logger.info(f"Summary: {news.summary}")
    
    logger.debug(f"Detailed handler processing news ID={news.id}")
    
    # Check for optional fields
    if hasattr(news, 'content') and news.content:
        logger.info(f"Content: {news.content[:200]}...")
        logger.debug(f"Content length: {len(news.content)} characters")
    
    if news.images:
        logger.info(f"Images: {len(news.images)}")
        for img in news.images:
            logger.info(f"  - {img.url} ({img.size})")
            logger.debug(f"Image details: url={img.url}, size={img.size}")
    
    logger.info("=" * 80)
    logger.info("")


# ============================================================================
# Example 3: Filtered Handler (only show news with specific keywords)
# ============================================================================

KEYWORDS = ["earnings", "acquisition", "merger", "SEC filing"]

async def filtered_news_handler(news: News):
    """Handler that only displays news matching specific keywords."""
    text = f"{news.headline} {news.summary}".lower()
    
    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in text]
    logger.debug(f"Filtered handler checking news ID={news.id} against keywords: {KEYWORDS}")
    
    if matched_keywords:
        logger.info(f"🔔 ALERT! Keywords matched: {', '.join(matched_keywords)}")
        logger.info(f"   {news.headline}")
        logger.info(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
        logger.info(f"   URL: {news.url}")
        logger.debug(f"News ID={news.id} matched {len(matched_keywords)} keyword(s)")
        logger.info("")
    else:
        logger.debug(f"News ID={news.id} did not match any keywords")


# ============================================================================
# Example 4: Statistics Tracker
# ============================================================================

class NewsStats:
    def __init__(self):
        self.total_count = 0
        self.by_source = {}
        self.by_symbol = {}
        self.start_time = datetime.now()

stats = NewsStats()

async def stats_news_handler(news: News):
    """Handler that tracks statistics about news articles."""
    stats.total_count += 1
    logger.debug(f"Stats handler processing news ID={news.id}, total count: {stats.total_count}")
    
    # Track by source
    stats.by_source[news.source] = stats.by_source.get(news.source, 0) + 1
    logger.debug(f"Updated source stats for '{news.source}': {stats.by_source[news.source]}")
    
    # Track by symbol
    if news.symbols:
        for symbol in news.symbols:
            stats.by_symbol[symbol] = stats.by_symbol.get(symbol, 0) + 1
            logger.debug(f"Updated symbol stats for '{symbol}': {stats.by_symbol[symbol]}")
    
    # Print stats every 10 articles
    if stats.total_count % 10 == 0:
        elapsed = (datetime.now() - stats.start_time).total_seconds()
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 NEWS STATISTICS (after {stats.total_count} articles in {elapsed:.0f}s)")
        logger.info("=" * 80)
        
        logger.info("\nTop 5 Sources:")
        top_sources = sorted(stats.by_source.items(), key=lambda x: x[1], reverse=True)[:5]
        for source, count in top_sources:
            logger.info(f"  {source}: {count}")
        
        logger.info("\nTop 10 Symbols:")
        top_symbols = sorted(stats.by_symbol.items(), key=lambda x: x[1], reverse=True)[:10]
        for symbol, count in top_symbols:
            logger.info(f"  {symbol}: {count}")
        
        logger.info("=" * 80)
        logger.info("")


# ============================================================================
# Example 5: Symbol-Specific Handler with Multiple Subscriptions
# ============================================================================

async def aapl_handler(news: News):
    """Handler specifically for AAPL news."""
    logger.info(f"🍎 APPLE NEWS: {news.headline}")
    logger.debug(f"AAPL handler processed news ID={news.id}")

async def tsla_handler(news: News):
    """Handler specifically for TSLA news."""
    logger.info(f"🚗 TESLA NEWS: {news.headline}")
    logger.debug(f"TSLA handler processed news ID={news.id}")

async def generic_handler(news: News):
    """Handler for other symbols."""
    logger.info(f"📰 NEWS: {news.headline}")
    logger.debug(f"Generic handler processed news ID={news.id}, symbols={news.symbols}")


# ============================================================================
# Main Function - Choose Your Example
# ============================================================================

def main():
    """
    Main function to run news streaming examples.
    Uncomment the example you want to run.
    """
    
    news_stream = NewsDataStream(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET_KEY")
    )
    logger.info("NewsDataStream initialized")
    
    logger.info("Alpaca News Streaming Examples")
    logger.info("=" * 80)
    
    # -------------------------------------------------------------------------
    # EXAMPLE 1: Basic news for specific symbols
    # -------------------------------------------------------------------------
    logger.info("\n🔹 Example 1: Basic news streaming for AAPL, TSLA, MSFT")
    symbols_example1 = ["AAPL", "TSLA", "MSFT"]
    news_stream.subscribe_news(basic_news_handler, *symbols_example1)
    logger.info(f"Subscribed to news for {len(symbols_example1)} symbols: {', '.join(symbols_example1)}")
    logger.debug(f"Example 1 active: basic_news_handler with symbols {symbols_example1}")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 2: Detailed news for specific symbols
    # -------------------------------------------------------------------------
    # logger.info("\n🔹 Example 2: Detailed news streaming for GOOGL, AMZN")
    # news_stream.subscribe_news(detailed_news_handler, "GOOGL", "AMZN")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 3: Filtered news (all symbols, but only show filtered content)
    # -------------------------------------------------------------------------
    # logger.info(f"\n🔹 Example 3: Filtered news (keywords: {', '.join(KEYWORDS)})")
    # news_stream.subscribe_news(filtered_news_handler, "*")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 4: News statistics tracker
    # -------------------------------------------------------------------------
    # logger.info("\n🔹 Example 4: News statistics tracker (all symbols)")
    # news_stream.subscribe_news(stats_news_handler, "*")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 5: Multiple handlers for different symbols
    # -------------------------------------------------------------------------
    # logger.info("\n🔹 Example 5: Symbol-specific handlers")
    # news_stream.subscribe_news(aapl_handler, "AAPL")
    # news_stream.subscribe_news(tsla_handler, "TSLA")
    # news_stream.subscribe_news(generic_handler, "MSFT", "GOOGL", "AMZN")
    
    logger.info("-" * 80)
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    try:
        logger.info("Starting news data stream event loop")
        news_stream.run()
    except KeyboardInterrupt:
        logger.info("\n\nStream stopped by user")
    except Exception as e:
        logger.error(f"Error in news stream examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
