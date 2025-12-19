from alpaca.data.live import NewsDataStream
from alpaca.data.models import News
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import re

# Load environment variables
load_dotenv()

# Initialize the news data stream
news_stream = NewsDataStream(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)

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
    # Check keyword filter
    if FILTER_KEYWORDS:
        text_to_search = f"{news.headline} {news.summary}".lower()
        if not any(keyword.lower() in text_to_search for keyword in FILTER_KEYWORDS):
            return False
    
    # Check minimum symbols count
    if news.symbols and len(news.symbols) < MIN_SYMBOLS_COUNT:
        return False
    
    # Check source filter
    if FILTER_SOURCES and news.source not in FILTER_SOURCES:
        return False
    
    return True


async def news_handler(news: News):
    """
    Handler function with filtering capabilities for processing incoming news data.
    
    Args:
        news (News): News article object containing headline, summary, symbols, etc.
    """
    # Apply filters
    if not matches_filter(news):
        return  # Skip this news article
    
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
    print("=" * 100)
    print(f"📰 FILTERED NEWS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"🔖 ID: {news.id}")
    print(f"📌 Headline: {highlight_keywords(news.headline)}")
    print(f"✍️  Author: {news.author}")
    print(f"🕐 Created: {news.created_at}")
    print(f"📊 Symbols ({len(news.symbols) if news.symbols else 0}): {', '.join(news.symbols) if news.symbols else 'N/A'}")
    print(f"📡 Source: {news.source}")
    print(f"🔗 URL: {news.url}")
    
    if news.summary:
        print(f"\n📝 Summary:")
        print(f"   {highlight_keywords(news.summary)}")
    
    # Display images if available
    if news.images:
        print(f"\n📷 Images: {len(news.images)} attached")
    
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
    Main function to start the filtered news data stream.
    Subscribes to news with filtering capabilities.
    """
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 25 + "ALPACA NEWS DATA STREAM (FILTERED)" + " " * 40 + "║")
    print("╚" + "=" * 98 + "╝")
    print()
    print(f"🚀 Starting Alpaca News Data Stream at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if SYMBOLS_TO_WATCH == ["*"]:
        print(f"📊 Subscribing to: ALL SYMBOLS")
    else:
        print(f"📊 Subscribing to news for {len(SYMBOLS_TO_WATCH)} symbols:")
        print(f"   {', '.join(SYMBOLS_TO_WATCH)}")
    
    print("\n🔍 Active Filters:")
    if FILTER_KEYWORDS:
        print(f"   Keywords: {', '.join(FILTER_KEYWORDS)}")
    if MIN_SYMBOLS_COUNT > 1:
        print(f"   Minimum symbols: {MIN_SYMBOLS_COUNT}")
    if FILTER_SOURCES:
        print(f"   Sources: {', '.join(FILTER_SOURCES)}")
    if not (FILTER_KEYWORDS or MIN_SYMBOLS_COUNT > 1 or FILTER_SOURCES):
        print(f"   No filters active (showing all news)")
    
    if SAVE_TO_FILE:
        print(f"\n💾 Saving news data to: {OUTPUT_FILE}")
    
    print("-" * 100)
    print("🎧 Listening for news... (Press Ctrl+C to stop)")
    print("-" * 100)
    print()
    
    # Subscribe to news for specific symbols or all symbols
    if SYMBOLS_TO_WATCH == ["*"]:
        news_stream.subscribe_news(news_handler, "*")
    else:
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
