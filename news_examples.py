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

# Load environment variables
load_dotenv()


# ============================================================================
# Example 1: Basic News Handler
# ============================================================================

async def basic_news_handler(news: News):
    """Simple handler that prints headline and symbols."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {news.headline}")
    print(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}\n")


# ============================================================================
# Example 2: Detailed News Handler
# ============================================================================

async def detailed_news_handler(news: News):
    """Handler that displays all available news data."""
    print("=" * 80)
    print(f"ID: {news.id}")
    print(f"Headline: {news.headline}")
    print(f"Author: {news.author}")
    print(f"Created: {news.created_at}")
    print(f"Updated: {news.updated_at}")
    print(f"Symbols: {news.symbols}")
    print(f"Source: {news.source}")
    print(f"URL: {news.url}")
    print(f"Summary: {news.summary}")
    
    # Check for optional fields
    if hasattr(news, 'content') and news.content:
        print(f"Content: {news.content[:200]}...")
    
    if news.images:
        print(f"Images: {len(news.images)}")
        for img in news.images:
            print(f"  - {img.url} ({img.size})")
    
    print("=" * 80 + "\n")


# ============================================================================
# Example 3: Filtered Handler (only show news with specific keywords)
# ============================================================================

KEYWORDS = ["earnings", "acquisition", "merger", "SEC filing"]

async def filtered_news_handler(news: News):
    """Handler that only displays news matching specific keywords."""
    text = f"{news.headline} {news.summary}".lower()
    
    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in text]
    
    if matched_keywords:
        print(f"🔔 ALERT! Keywords matched: {', '.join(matched_keywords)}")
        print(f"   {news.headline}")
        print(f"   Symbols: {', '.join(news.symbols) if news.symbols else 'N/A'}")
        print(f"   URL: {news.url}\n")


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
    
    # Track by source
    stats.by_source[news.source] = stats.by_source.get(news.source, 0) + 1
    
    # Track by symbol
    if news.symbols:
        for symbol in news.symbols:
            stats.by_symbol[symbol] = stats.by_symbol.get(symbol, 0) + 1
    
    # Print stats every 10 articles
    if stats.total_count % 10 == 0:
        elapsed = (datetime.now() - stats.start_time).total_seconds()
        print("\n" + "=" * 80)
        print(f"📊 NEWS STATISTICS (after {stats.total_count} articles in {elapsed:.0f}s)")
        print("=" * 80)
        
        print("\nTop 5 Sources:")
        top_sources = sorted(stats.by_source.items(), key=lambda x: x[1], reverse=True)[:5]
        for source, count in top_sources:
            print(f"  {source}: {count}")
        
        print("\nTop 10 Symbols:")
        top_symbols = sorted(stats.by_symbol.items(), key=lambda x: x[1], reverse=True)[:10]
        for symbol, count in top_symbols:
            print(f"  {symbol}: {count}")
        
        print("=" * 80 + "\n")


# ============================================================================
# Example 5: Symbol-Specific Handler with Multiple Subscriptions
# ============================================================================

async def aapl_handler(news: News):
    """Handler specifically for AAPL news."""
    print(f"🍎 APPLE NEWS: {news.headline}")

async def tsla_handler(news: News):
    """Handler specifically for TSLA news."""
    print(f"🚗 TESLA NEWS: {news.headline}")

async def generic_handler(news: News):
    """Handler for other symbols."""
    print(f"📰 NEWS: {news.headline}")


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
    
    print("Alpaca News Streaming Examples")
    print("=" * 80)
    
    # -------------------------------------------------------------------------
    # EXAMPLE 1: Basic news for specific symbols
    # -------------------------------------------------------------------------
    print("\n🔹 Example 1: Basic news streaming for AAPL, TSLA, MSFT")
    news_stream.subscribe_news(basic_news_handler, "AAPL", "TSLA", "MSFT")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 2: Detailed news for specific symbols
    # -------------------------------------------------------------------------
    # print("\n🔹 Example 2: Detailed news streaming for GOOGL, AMZN")
    # news_stream.subscribe_news(detailed_news_handler, "GOOGL", "AMZN")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 3: Filtered news (all symbols, but only show filtered content)
    # -------------------------------------------------------------------------
    # print(f"\n🔹 Example 3: Filtered news (keywords: {', '.join(KEYWORDS)})")
    # news_stream.subscribe_news(filtered_news_handler, "*")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 4: News statistics tracker
    # -------------------------------------------------------------------------
    # print("\n🔹 Example 4: News statistics tracker (all symbols)")
    # news_stream.subscribe_news(stats_news_handler, "*")
    
    # -------------------------------------------------------------------------
    # EXAMPLE 5: Multiple handlers for different symbols
    # -------------------------------------------------------------------------
    # print("\n🔹 Example 5: Symbol-specific handlers")
    # news_stream.subscribe_news(aapl_handler, "AAPL")
    # news_stream.subscribe_news(tsla_handler, "TSLA")
    # news_stream.subscribe_news(generic_handler, "MSFT", "GOOGL", "AMZN")
    
    print("-" * 80)
    print("Press Ctrl+C to stop\n")
    
    try:
        news_stream.run()
    except KeyboardInterrupt:
        print("\n\nStream stopped by user")


if __name__ == "__main__":
    main()
