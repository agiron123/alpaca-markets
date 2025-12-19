#!/usr/bin/env python3
"""
Historical Cryptocurrency Data Fetcher

Fetches historical cryptocurrency bar data from Alpaca Markets API
and exports it to CSV format with rate limit handling.
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.common.exceptions import APIError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limit configuration
DEFAULT_RATE_LIMIT_DELAY = 0.4  # seconds between requests (conservative: ~2.5 req/sec)
BASIC_PLAN_LIMIT = 200  # requests per minute
REQUESTS_PER_SECOND_LIMIT = 3.0  # conservative limit


def parse_date(date_string: str) -> datetime:
    """Parse date string in YYYY-MM-DD format to datetime object."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_string}. Expected YYYY-MM-DD format.") from e


def parse_granularity(granularity: str) -> TimeFrame:
    """Parse granularity string to TimeFrame enum."""
    granularity_map = {
        "minute": TimeFrame.Minute,
        "hour": TimeFrame.Hour,
        "day": TimeFrame.Day,
        "week": TimeFrame.Week,
        "month": TimeFrame.Month,
    }
    granularity_lower = granularity.lower()
    if granularity_lower not in granularity_map:
        valid_options = ", ".join(granularity_map.keys())
        raise ValueError(
            f"Invalid granularity: {granularity}. "
            f"Valid options are: {valid_options}"
        )
    return granularity_map[granularity_lower]


def generate_output_filename(symbol: str, granularity: str, start: str, end: str) -> str:
    """Generate default output filename from parameters."""
    # Replace / with _ in symbol for filename safety
    safe_symbol = symbol.replace("/", "_")
    return f"{safe_symbol}_{granularity}_{start}_{end}.csv"


def fetch_historical_data(
    client: CryptoHistoricalDataClient,
    symbol: str,
    start: datetime,
    end: datetime,
    timeframe: TimeFrame,
    rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
) -> pd.DataFrame:
    """
    Fetch historical cryptocurrency bar data with pagination and rate limiting.
    
    Args:
        client: CryptoHistoricalDataClient instance
        symbol: Cryptocurrency symbol (e.g., "BTC/USD")
        start: Start datetime
        end: End datetime
        timeframe: TimeFrame enum for granularity
        rate_limit_delay: Delay in seconds between requests
        
    Returns:
        pandas DataFrame with historical bar data
    """
    all_bars = []
    current_start = start
    
    logger.info(
        f"Fetching historical data for {symbol} from {start.date()} to {end.date()} "
        f"with {timeframe} granularity"
    )
    
    request_count = 0
    max_bars_per_request = 10000  # Alpaca's typical limit per request
    
    while current_start < end:
        request_count += 1
        logger.debug(f"Request #{request_count}: Fetching from {current_start.date()}")
        
        # Calculate request end date (limit to avoid hitting max bars limit)
        # For minute data, limit to ~7 days per request (to stay under 10k bars)
        # For hour data, limit to ~416 days per request (24 hours * 416 = ~10k bars)
        # For day/week/month data, can request larger ranges
        if timeframe == TimeFrame.Minute:
            # ~7 days for minute data (7 * 24 * 60 = 10,080 minutes, slightly over but safe)
            request_end = min(current_start + timedelta(days=7), end)
        elif timeframe == TimeFrame.Hour:
            # ~416 days for hour data (416 * 24 = 9,984 hours)
            request_end = min(current_start + timedelta(days=416), end)
        else:
            # For day/week/month, request the full range (much fewer bars)
            request_end = end
        
        # Safety check: ensure request_end is after current_start
        if request_end <= current_start:
            logger.warning(f"Request end date ({request_end}) is not after start date ({current_start}). Breaking loop.")
            break
        
        try:
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=timeframe,
                start=current_start,
                end=request_end,
            )
            
            # Apply rate limiting
            if request_count > 1:
                logger.debug(f"Rate limiting: waiting {rate_limit_delay}s before next request")
                time.sleep(rate_limit_delay)
            
            bars = client.get_crypto_bars(request_params)
            
            # Convert to DataFrame
            if bars and symbol in bars:
                symbol_bars = bars[symbol]
                if len(symbol_bars) > 0:
                    bars_df = symbol_bars.df
                    all_bars.append(bars_df)
                    logger.info(
                        f"Fetched {len(symbol_bars)} bars for {symbol} "
                        f"(from {current_start.date()} to {request_end.date()})"
                    )
                else:
                    logger.warning(f"No bars returned for {symbol} in date range {current_start.date()} to {request_end.date()}")
            else:
                logger.warning(f"No data returned for {symbol} in date range {current_start.date()} to {request_end.date()}")
            
            # Move to next period
            current_start = request_end
            
            # If we got fewer bars than expected, we might have reached the end
            if bars and symbol in bars and len(bars[symbol]) < max_bars_per_request:
                # Likely reached the end of available data
                if request_end >= end:
                    break
                    
        except APIError as e:
            logger.error(f"API error while fetching data: {e}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                logger.warning("Rate limit hit. Waiting 60 seconds before retry...")
                time.sleep(60)
                continue
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching data: {e}", exc_info=True)
            raise
    
    if not all_bars:
        logger.warning(f"No data was fetched for {symbol}")
        return pd.DataFrame()
    
    # Combine all DataFrames
    combined_df = pd.concat(all_bars, ignore_index=True)
    
    # Sort by timestamp
    if 'timestamp' in combined_df.columns:
        combined_df = combined_df.sort_values('timestamp')
    
    logger.info(f"Total bars fetched: {len(combined_df)}")
    return combined_df


def format_dataframe_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame for CSV export with standard OHLCV columns.
    
    Args:
        df: DataFrame with bar data
        
    Returns:
        Formatted DataFrame ready for CSV export
    """
    if df.empty:
        return df
    
    # Select and rename columns to standard format
    column_mapping = {
        'timestamp': 'timestamp',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume',
    }
    
    # Find available columns
    available_columns = {}
    for standard_col, possible_col in column_mapping.items():
        if possible_col in df.columns:
            available_columns[standard_col] = possible_col
    
    if not available_columns:
        logger.warning("No recognized columns found in DataFrame")
        return df
    
    # Select and rename columns
    formatted_df = df[list(available_columns.values())].copy()
    formatted_df = formatted_df.rename(columns={v: k for k, v in available_columns.items()})
    
    # Ensure timestamp is in ISO format string
    if 'timestamp' in formatted_df.columns:
        if pd.api.types.is_datetime64_any_dtype(formatted_df['timestamp']):
            formatted_df['timestamp'] = formatted_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif formatted_df['timestamp'].dtype == 'object':
            # If it's already a string, try to parse and reformat if needed
            try:
                # Try to parse as datetime and reformat
                parsed = pd.to_datetime(formatted_df['timestamp'])
                formatted_df['timestamp'] = parsed.dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, TypeError):
                # If parsing fails, keep original format
                logger.debug("Could not parse timestamp column, keeping original format")
                pass
    
    # Reorder columns to standard OHLCV format
    column_order = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    existing_columns = [col for col in column_order if col in formatted_df.columns]
    formatted_df = formatted_df[existing_columns]
    
    return formatted_df


def export_to_csv(df: pd.DataFrame, output_file: str) -> None:
    """
    Export DataFrame to CSV file.
    
    Args:
        df: DataFrame to export
        output_file: Output file path
    """
    try:
        df.to_csv(output_file, index=False)
        logger.info(f"Successfully exported {len(df)} rows to {output_file}")
    except Exception as e:
        logger.error(f"Error writing CSV file {output_file}: {e}", exc_info=True)
        raise


def main():
    """Main function to run the historical data fetcher."""
    parser = argparse.ArgumentParser(
        description="Fetch historical cryptocurrency pricing data from Alpaca Markets API"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Cryptocurrency symbol (e.g., BTC/USD, ETH/USD)"
    )
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--granularity",
        type=str,
        required=True,
        choices=["minute", "hour", "day", "week", "month"],
        help="Time granularity (minute, hour, day, week, month)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV filename (default: {symbol}_{granularity}_{start}_{end}.csv)"
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=DEFAULT_RATE_LIMIT_DELAY,
        help=f"Delay in seconds between API requests (default: {DEFAULT_RATE_LIMIT_DELAY})"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    logger.debug("Environment variables loaded")
    
    # Validate and parse dates
    try:
        start_date = parse_date(args.start)
        end_date = parse_date(args.end)
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        sys.exit(1)
    
    if start_date >= end_date:
        logger.error("Start date must be before end date")
        sys.exit(1)
    
    # Parse granularity
    try:
        timeframe = parse_granularity(args.granularity)
    except ValueError as e:
        logger.error(f"Granularity error: {e}")
        sys.exit(1)
    
    # Generate output filename if not provided
    output_file = args.output
    if output_file is None:
        output_file = generate_output_filename(
            args.symbol, args.granularity, args.start, args.end
        )
    
    # Initialize Alpaca client
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        logger.warning(
            "API keys not found in environment. "
            "Historical data may be accessible without keys, but rate limits will be lower."
        )
        client = CryptoHistoricalDataClient()
    else:
        logger.info("Initializing CryptoHistoricalDataClient with API keys")
        client = CryptoHistoricalDataClient(api_key=api_key, secret_key=secret_key)
    
    # Fetch historical data
    try:
        df = fetch_historical_data(
            client=client,
            symbol=args.symbol,
            start=start_date,
            end=end_date,
            timeframe=timeframe,
            rate_limit_delay=args.rate_limit_delay,
        )
    except Exception as e:
        logger.error(f"Failed to fetch historical data: {e}", exc_info=True)
        sys.exit(1)
    
    if df.empty:
        logger.warning("No data was fetched. Exiting without creating CSV file.")
        sys.exit(0)
    
    # Format DataFrame for CSV
    formatted_df = format_dataframe_for_csv(df)
    
    # Export to CSV
    try:
        export_to_csv(formatted_df, output_file)
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Historical data fetch completed successfully")


if __name__ == "__main__":
    main()
