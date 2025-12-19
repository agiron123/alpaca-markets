# Alpaca News Data Model Reference

## News Object Attributes

When you receive a news article through the Alpaca News Data Stream, it comes as a `News` object with the following attributes:

### Core Attributes

- **`id`** (int): Unique identifier for the news article
- **`headline`** (str): The headline/title of the news article
- **`author`** (str): Author of the article
- **`created_at`** (datetime): Timestamp when the article was created
- **`updated_at`** (datetime): Timestamp when the article was last updated
- **`source`** (str): News source (e.g., "Bloomberg", "Reuters", "Benzinga")
- **`url`** (str): URL to the full article
- **`summary`** (str): Brief summary of the article
- **`symbols`** (list[str]): List of stock symbols mentioned in the article (e.g., ["AAPL", "MSFT"])

### Optional Attributes

- **`content`** (str): Full article content (may not always be available)
- **`images`** (list[NewsImage]): List of images associated with the article

### NewsImage Object

If the news article has images, each image object contains:

- **`url`** (str): URL to the image
- **`size`** (str): Size descriptor (e.g., "small", "large", "thumb")

## Example Usage

```python
async def my_news_handler(news: News):
    # Access core attributes
    print(f"Headline: {news.headline}")
    print(f"Symbols: {news.symbols}")
    print(f"Source: {news.source}")
    print(f"URL: {news.url}")
    print(f"Created: {news.created_at}")
    
    # Check for optional attributes
    if hasattr(news, 'content') and news.content:
        print(f"Content: {news.content}")
    
    if news.images:
        for image in news.images:
            print(f"Image: {image.url} ({image.size})")
```

## Subscription Patterns

### Subscribe to Specific Symbols

```python
news_stream.subscribe_news(handler, "AAPL", "TSLA", "MSFT")
```

### Subscribe to All News

```python
news_stream.subscribe_news(handler, "*")
```

### Multiple Handlers for Different Symbols

```python
news_stream.subscribe_news(aapl_handler, "AAPL")
news_stream.subscribe_news(tsla_handler, "TSLA")
news_stream.subscribe_news(general_handler, "MSFT", "GOOGL")
```

## Common Tasks

### Filter by Keywords

```python
async def filtered_handler(news: News):
    keywords = ["earnings", "acquisition", "merger"]
    text = f"{news.headline} {news.summary}".lower()
    
    if any(keyword.lower() in text for keyword in keywords):
        print(f"Matched: {news.headline}")
```

### Save to JSON

```python
import json

async def save_handler(news: News):
    data = {
        "id": news.id,
        "headline": news.headline,
        "symbols": news.symbols,
        "source": news.source,
        "created_at": str(news.created_at),
        "url": news.url
    }
    
    with open("news.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
```

### Track Statistics

```python
stats = {"total": 0, "by_symbol": {}}

async def stats_handler(news: News):
    stats["total"] += 1
    
    if news.symbols:
        for symbol in news.symbols:
            stats["by_symbol"][symbol] = stats["by_symbol"].get(symbol, 0) + 1
    
    if stats["total"] % 10 == 0:
        print(f"Processed {stats['total']} articles")
        print(f"Top symbols: {sorted(stats['by_symbol'].items(), key=lambda x: x[1], reverse=True)[:5]}")
```

## Tips and Best Practices

1. **Handle Optional Fields**: Always check if optional attributes exist before accessing them using `hasattr()` or try/except
2. **Use Wildcards Wisely**: Subscribing to all symbols (`"*"`) can generate a high volume of data
3. **Implement Filtering**: Apply filters in your handler to focus on relevant news
4. **Error Handling**: Wrap your handler logic in try/except to prevent crashes
5. **Rate Limiting**: Be aware of API rate limits when processing high volumes of news
6. **Async Handlers**: All handlers must be async functions (use `async def`)

## Error Handling Example

```python
async def safe_handler(news: News):
    try:
        # Your processing logic here
        print(f"Processing: {news.headline}")
        
        # Safe access to optional fields
        content = getattr(news, 'content', None)
        if content:
            print(f"Content available: {len(content)} characters")
            
    except Exception as e:
        print(f"Error processing news {news.id}: {e}")
```
