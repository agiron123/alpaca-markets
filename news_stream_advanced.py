from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
from datetime import datetime
import json
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
SYMBOLS_TO_WATCH = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "NFLX"]
SAVE_TO_FILE = True
OUTPUT_FILE = "news_feed.jsonl"


async def news_handler(news: News):
    """
    Advanced handler function for processing incoming news data.
    Displays formatted news and optionally saves to file.
    
    Args:
        news (News): News article object containing headline, summary, symbols, etc.
    """
    logger.debug(f"Processing news article: ID={news.id}, Headline={news.headline[:50]}...")
    
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
    
    logger.debug(f"Formatted news data: {len(json.dumps(news_data))} bytes")
    
    # Display formatted output
    logger.info("=" * 100)
    logger.info(f"📰 NEWS ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 100)
    logger.info(f"🔖 ID: {news.id}")
    logger.info(f"📌 Headline: {news.headline}")
    logger.info(f"✍️  Author: {news.author}")
    logger.info(f"🕐 Created: {news.created_at}")
    logger.info(f"🕑 Updated: {news.updated_at}")
    logger.info(f"📊 Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    logger.info(f"📡 Source: {news.source}")
    logger.info(f"🔗 URL: {news.url}")
    
    if news.summary:
        logger.info(f"\n📝 Summary:")
        logger.info(f"   {news.summary}")
        logger.debug(f"Summary length: {len(news.summary)} characters")
    
    # Display content if available
    content = getattr(news, 'content', None)
    if content:
        logger.info(f"\n📄 Content:")
        # Truncate content if too long
        if len(content) > 500:
            logger.info(f"   {content[:500]}... (truncated)")
            logger.debug(f"Content truncated from {len(content)} to 500 characters")
        else:
            logger.info(f"   {content}")
            logger.debug(f"Full content displayed: {len(content)} characters")
    
    # Display images if available
    if news.images:
        logger.info(f"\n📷 Images ({len(news.images)}):")
        for idx, image in enumerate(news.images, 1):
            logger.info(f"   {idx}. {image.url} (Size: {image.size})")
            logger.debug(f"Image {idx}: url={image.url}, size={image.size}")
    
    logger.info("=" * 100)
    logger.info("")
    
    # Save to file if enabled
    if SAVE_TO_FILE:
        try:
            with open(OUTPUT_FILE, 'a') as f:
                f.write(json.dumps(news_data) + '\n')
            logger.debug(f"Successfully saved news article {news.id} to {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"Error saving to file {OUTPUT_FILE}: {e}", exc_info=True)


def main():
    """
    Main function to start the advanced news data stream.
    Subscribes to news for multiple symbols and starts the stream.
    """
    logger.info("╔" + "=" * 98 + "╗")
    logger.info("║" + " " * 30 + "ALPACA NEWS DATA STREAM" + " " * 45 + "║")
    logger.info("╚" + "=" * 98 + "╝")
    logger.info("")
    logger.info(f"🚀 Starting Alpaca News Data Stream at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📊 Subscribing to news for {len(SYMBOLS_TO_WATCH)} symbols:")
    logger.info(f"   {', '.join(SYMBOLS_TO_WATCH)}")
    logger.debug(f"Configuration: SAVE_TO_FILE={SAVE_TO_FILE}, OUTPUT_FILE={OUTPUT_FILE}")
    
    if SAVE_TO_FILE:
        logger.info(f"💾 Saving news data to: {OUTPUT_FILE}")
    
    logger.info("-" * 100)
    logger.info("🎧 Listening for news... (Press Ctrl+C to stop)")
    logger.info("-" * 100)
    logger.info("")
    
    try:
        # Subscribe to news for specific symbols
        news_stream.subscribe_news(news_handler, *SYMBOLS_TO_WATCH)
        logger.info(f"Successfully subscribed to news for {len(SYMBOLS_TO_WATCH)} symbols")
        
        # Start the stream
        logger.info("Starting news data stream event loop")
        news_stream.run()
    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 100)
        logger.info("🛑 News stream stopped by user")
        logger.info("=" * 100)
    except Exception as e:
        logger.error(f"Error occurred in news stream: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
