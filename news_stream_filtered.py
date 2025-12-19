from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import re
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
logger.info("NewsDataStream initialized")

# Configuration
SYMBOLS_TO_WATCH = ["*"]  # Use "*" to subscribe to all news
SAVE_TO_FILE = True
OUTPUT_FILE = "filtered_news.jsonl"

# Filtering configuration
FILTER_KEYWORDS = ["earnings", "revenue", "profit", "acquisition", "merger", "SEC", "FDA"]
MIN_SYMBOLS_COUNT = 1  # Only show news that mentions at least this many symbols
FILTER_SOURCES = []  # Optional: Filter by specific sources (e.g., ["Bloomberg", "Reuters"])


def matches_filter(news: News) -> bool:
    """
    Check if the news article matches our filtering criteria.
    
    Args:
        news (News): News article object
        
    Returns:
        bool: True if the news matches filters, False otherwise
    """
    logger.debug(f"Checking filter for news ID={news.id}, headline={news.headline[:50]}...")
    
    # Check keyword filter
    if FILTER_KEYWORDS:
        text_to_search = f"{news.headline} {news.summary}".lower()
        matched_keywords = [kw for kw in FILTER_KEYWORDS if kw.lower() in text_to_search]
        if not matched_keywords:
            logger.debug(f"News {news.id} filtered out: no keyword matches (searched: {FILTER_KEYWORDS})")
            return False
        logger.debug(f"News {news.id} matched keywords: {matched_keywords}")
    
    # Check minimum symbols count
    if news.symbols and len(news.symbols) < MIN_SYMBOLS_COUNT:
        logger.debug(f"News {news.id} filtered out: only {len(news.symbols)} symbol(s), required {MIN_SYMBOLS_COUNT}")
        return False
    
    # Check source filter
    if FILTER_SOURCES and news.source not in FILTER_SOURCES:
        logger.debug(f"News {news.id} filtered out: source '{news.source}' not in allowed sources {FILTER_SOURCES}")
        return False
    
    logger.debug(f"News {news.id} passed all filters")
    return True


async def news_handler(news: News):
    """
    Handler function with filtering capabilities for processing incoming news data.
    
    Args:
        news (News): News article object containing headline, summary, symbols, etc.
    """
    logger.debug(f"Received news article: ID={news.id}, headline={news.headline[:50]}...")
    
    # Apply filters
    if not matches_filter(news):
        logger.warning(f"News article filtered out: ID={news.id}, headline={news.headline[:50]}...")
        return  # Skip this news article
    
    logger.info(f"News article passed filters: ID={news.id}, headline={news.headline[:50]}...")
    
    # Format the news data
    news_data = {
        "id": news.id,
        "headline": news.headline,
        "author": news.author,
        "created_at": str(news.created_at),
        "updated_at": str(news.updated_at),
        "symbols": news.symbols,
        "source": news.source,
        "url": news.url,
        "summary": news.summary,
        "content": getattr(news, 'content', None),
        "images": [{"url": img.url, "size": img.size} for img in news.images] if news.images else []
    }
    
    # Highlight matched keywords in headline and summary
    def highlight_keywords(text):
        if not text or not FILTER_KEYWORDS:
            return text
        
        highlighted = text
        for keyword in FILTER_KEYWORDS:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(f"**{keyword.upper()}**", highlighted)
        return highlighted
    
    # Display formatted output
    logger.info("=" * 100)
    logger.info(f"📰 FILTERED NEWS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 100)
    logger.info(f"🔖 ID: {news.id}")
    logger.info(f"📌 Headline: {highlight_keywords(news.headline)}")
    logger.info(f"✍️  Author: {news.author}")
    logger.info(f"🕐 Created: {news.created_at}")
    logger.info(f"📊 Symbols ({len(news.symbols) if news.symbols else 0}): {', '.join(news.symbols) if news.symbols else 'N/A'}")
    logger.info(f"📡 Source: {news.source}")
    logger.info(f"🔗 URL: {news.url}")
    
    logger.debug(f"News data formatted: {len(json.dumps(news_data))} bytes")
    
    if news.summary:
        logger.info(f"\n📝 Summary:")
        logger.info(f"   {highlight_keywords(news.summary)}")
        logger.debug(f"Summary length: {len(news.summary)} characters")
    
    # Display images if available
    if news.images:
        logger.info(f"\n📷 Images: {len(news.images)} attached")
        logger.debug(f"Image count: {len(news.images)}")
    
    logger.info("=" * 100)
    logger.info("")
    
    # Save to file if enabled
    if SAVE_TO_FILE:
        try:
            with open(OUTPUT_FILE, 'a') as f:
                f.write(json.dumps(news_data) + '\n')
            logger.debug(f"Successfully saved filtered news article {news.id} to {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"Error saving to file {OUTPUT_FILE}: {e}", exc_info=True)


def main():
    """
    Main function to start the filtered news data stream.
    Subscribes to news with filtering capabilities.
    """
    logger.info("╔" + "=" * 98 + "╗")
    logger.info("║" + " " * 25 + "ALPACA NEWS DATA STREAM (FILTERED)" + " " * 40 + "║")
    logger.info("╚" + "=" * 98 + "╝")
    logger.info("")
    logger.info(f"🚀 Starting Alpaca News Data Stream at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if SYMBOLS_TO_WATCH == ["*"]:
        logger.info(f"📊 Subscribing to: ALL SYMBOLS")
        logger.debug("Subscribing to all symbols (wildcard)")
    else:
        logger.info(f"📊 Subscribing to news for {len(SYMBOLS_TO_WATCH)} symbols:")
        logger.info(f"   {', '.join(SYMBOLS_TO_WATCH)}")
        logger.debug(f"Symbol list: {SYMBOLS_TO_WATCH}")
    
    logger.info("\n🔍 Active Filters:")
    if FILTER_KEYWORDS:
        logger.info(f"   Keywords: {', '.join(FILTER_KEYWORDS)}")
        logger.debug(f"Keyword filter: {FILTER_KEYWORDS}")
    if MIN_SYMBOLS_COUNT > 1:
        logger.info(f"   Minimum symbols: {MIN_SYMBOLS_COUNT}")
        logger.debug(f"Minimum symbols filter: {MIN_SYMBOLS_COUNT}")
    if FILTER_SOURCES:
        logger.info(f"   Sources: {', '.join(FILTER_SOURCES)}")
        logger.debug(f"Source filter: {FILTER_SOURCES}")
    if not (FILTER_KEYWORDS or MIN_SYMBOLS_COUNT > 1 or FILTER_SOURCES):
        logger.info(f"   No filters active (showing all news)")
        logger.debug("No active filters configured")
    
    if SAVE_TO_FILE:
        logger.info(f"\n💾 Saving news data to: {OUTPUT_FILE}")
        logger.debug(f"File output enabled: {OUTPUT_FILE}")
    
    logger.info("-" * 100)
    logger.info("🎧 Listening for news... (Press Ctrl+C to stop)")
    logger.info("-" * 100)
    logger.info("")
    
    try:
        # Subscribe to news for specific symbols or all symbols
        if SYMBOLS_TO_WATCH == ["*"]:
            news_stream.subscribe_news(news_handler, "*")
            logger.info("Successfully subscribed to all news with filtering")
        else:
            news_stream.subscribe_news(news_handler, *SYMBOLS_TO_WATCH)
            logger.info(f"Successfully subscribed to news for {len(SYMBOLS_TO_WATCH)} symbols with filtering")
        
        # Start the stream
        logger.info("Starting filtered news data stream event loop")
        news_stream.run()
    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 100)
        logger.info("🛑 News stream stopped by user")
        logger.info("=" * 100)
    except Exception as e:
        logger.error(f"Error occurred in filtered news stream: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
