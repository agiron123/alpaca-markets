from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
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


async def news_handler(news: News):
    """
    Handler function for processing incoming news data.
    
    Args:
        news (News): News article object containing headline, summary, symbols, etc.
    """
    logger.info("=" * 80)
    logger.info("📰 NEWS ALERT")
    logger.info("=" * 80)
    logger.info(f"Headline: {news.headline}")
    logger.info(f"Author: {news.author}")
    logger.info(f"Created: {news.created_at}")
    logger.info(f"Updated: {news.updated_at}")
    logger.info(f"Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    logger.info(f"Source: {news.source}")
    logger.info(f"URL: {news.url}")
    logger.info(f"\nSummary: {news.summary}")
    
    logger.debug(f"News ID: {news.id}")
    logger.debug(f"News content available: {hasattr(news, 'content')}")
    
    # Display images if available
    if news.images:
        logger.info(f"\n📷 Images ({len(news.images)}):")
        for idx, image in enumerate(news.images, 1):
            logger.info(f"  {idx}. {image.url} (Size: {image.size})")
            logger.debug(f"Image {idx} details: url={image.url}, size={image.size}")
    
    logger.info("=" * 80)
    logger.info("")


def main():
    """
    Main function to start the news data stream.
    Subscribes to news for specific symbols and starts the stream.
    """
    logger.info("Starting Alpaca News Data Stream...")
    symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    logger.info(f"Subscribing to news for: {', '.join(symbols)}")
    logger.info("-" * 80)
    
    try:
        # Subscribe to news for specific symbols
        # You can add more symbols or use "*" to subscribe to all news
        news_stream.subscribe_news(news_handler, *symbols)
        logger.info(f"Successfully subscribed to news for {len(symbols)} symbols")
        
        # Start the stream
        logger.info("Starting news data stream event loop")
        news_stream.run()
    except Exception as e:
        logger.error(f"Error in news stream: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
