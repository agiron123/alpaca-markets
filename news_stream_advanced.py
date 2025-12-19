from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Initialize the news data stream
news_stream = NewsDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)

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
    
    # Display formatted output
    print("=" * 100)
    print(f"📰 NEWS ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"🔖 ID: {news.id}")
    print(f"📌 Headline: {news.headline}")
    print(f"✍️  Author: {news.author}")
    print(f"🕐 Created: {news.created_at}")
    print(f"🕑 Updated: {news.updated_at}")
    print(f"📊 Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
    print(f"📡 Source: {news.source}")
    print(f"🔗 URL: {news.url}")
    
    if news.summary:
        print(f"\n📝 Summary:")
        print(f"   {news.summary}")
    
    # Display content if available
    content = getattr(news, 'content', None)
    if content:
        print(f"\n📄 Content:")
        # Truncate content if too long
        if len(content) > 500:
            print(f"   {content[:500]}... (truncated)")
        else:
            print(f"   {content}")
    
    # Display images if available
    if news.images:
        print(f"\n📷 Images ({len(news.images)}):")
        for idx, image in enumerate(news.images, 1):
            print(f"   {idx}. {image.url} (Size: {image.size})")
    
    print("=" * 100)
    print()
    
    # Save to file if enabled
    if SAVE_TO_FILE:
        try:
            with open(OUTPUT_FILE, 'a') as f:
                f.write(json.dumps(news_data) + '\n')
        except Exception as e:
            print(f"⚠️  Error saving to file: {e}")


def main():
    """
    Main function to start the advanced news data stream.
    Subscribes to news for multiple symbols and starts the stream.
    """
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 30 + "ALPACA NEWS DATA STREAM" + " " * 45 + "║")
    print("╚" + "=" * 98 + "╝")
    print()
    print(f"🚀 Starting Alpaca News Data Stream at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Subscribing to news for {len(SYMBOLS_TO_WATCH)} symbols:")
    print(f"   {', '.join(SYMBOLS_TO_WATCH)}")
    
    if SAVE_TO_FILE:
        print(f"💾 Saving news data to: {OUTPUT_FILE}")
    
    print("-" * 100)
    print("🎧 Listening for news... (Press Ctrl+C to stop)")
    print("-" * 100)
    print()
    
    # Subscribe to news for specific symbols
    news_stream.subscribe_news(news_handler, *SYMBOLS_TO_WATCH)
    
    try:
        # Start the stream
        news_stream.run()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 100)
        print("🛑 News stream stopped by user")
        print("=" * 100)
    except Exception as e:
        print(f"\n\n⚠️  Error occurred: {e}")


if __name__ == "__main__":
    main()
