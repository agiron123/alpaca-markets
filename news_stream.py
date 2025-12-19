from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the news data stream
news_stream = NewsDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)


async def news_handler(news: News):
    """
    Handler function for processing incoming news data.
    
    Args:
        news (News): News article object containing headline, summary, symbols, etc.
    """
    print("=" * 80)
    print(f"📰 NEWS ALERT")
    print("=" * 80)
    print(f"Headline: {news.headline}")
    print(f"Author: {news.author}")
    print(f"Created: {news.created_at}")
    print(f"Updated: {news.updated_at}")
    print(f"Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    print(f"Source: {news.source}")
    print(f"URL: {news.url}")
    print(f"\nSummary: {news.summary}")
    
    # Display images if available
    if news.images:
        print(f"\n📷 Images ({len(news.images)}):")
        for idx, image in enumerate(news.images, 1):
            print(f"  {idx}. {image.url} (Size: {image.size})")
    
    print("=" * 80)
    print()


def main():
    """
    Main function to start the news data stream.
    Subscribes to news for specific symbols and starts the stream.
    """
    print("Starting Alpaca News Data Stream...")
    print("Subscribing to news for: AAPL, TSLA, MSFT, GOOGL, AMZN")
    print("-" * 80)
    
    # Subscribe to news for specific symbols
    # You can add more symbols or use "*" to subscribe to all news
    news_stream.subscribe_news(news_handler, "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN")
    
    # Start the stream
    news_stream.run()


if __name__ == "__main__":
    main()
