from __future__ import annotations

import math
import os
import time
import logging
from collections import deque

from alpaca.common.exceptions import APIError
from alpaca.data.live import CryptoDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SYMBOL_BTC = "BTC/USD"
SYMBOL_SOL = "SOL/USD"

WINDOW_SIZE = 60  # 60 x 1-min bars ~= 1 hour
ENTRY_Z = 2.0
EXIT_Z = 0.5
TRADE_NOTIONAL_USD = 50.0
ALLOW_SHORT = False
MIN_SECONDS_BETWEEN_TRADES = 30


def _bar_symbol(bar) -> str:
    return getattr(bar, "symbol", None) or getattr(bar, "S", None)


def _bar_close(bar) -> float:
    return getattr(bar, "close", None) or getattr(bar, "c", None)


def _bar_time(bar):
    return getattr(bar, "timestamp", None) or getattr(bar, "t", None)


class RollingPairModel:
    def __init__(self, window_size: int) -> None:
        self._btc_log = deque(maxlen=window_size)
        self._sol_log = deque(maxlen=window_size)
        logger.debug(f"RollingPairModel initialized with window_size={window_size}")

    def update(self, btc_close: float, sol_close: float) -> None:
        self._btc_log.append(math.log(btc_close))
        self._sol_log.append(math.log(sol_close))
        logger.debug(f"Model updated: btc_log={math.log(btc_close):.6f}, sol_log={math.log(sol_close):.6f}, window_fill={len(self._btc_log)}/{self._btc_log.maxlen}")

    def ready(self) -> bool:
        is_ready = len(self._btc_log) == self._btc_log.maxlen
        if is_ready:
            logger.debug(f"Model is ready: window fully filled ({len(self._btc_log)}/{self._btc_log.maxlen})")
        return is_ready

    def compute_signal(self):
        n = len(self._btc_log)
        if n == 0:
            logger.debug("Signal computation skipped: no data in model")
            return None

        btc_mean = sum(self._btc_log) / n
        sol_mean = sum(self._sol_log) / n
        btc_var = sum((x - btc_mean) ** 2 for x in self._btc_log) / n
        logger.debug(f"Model stats: n={n}, btc_mean={btc_mean:.6f}, sol_mean={sol_mean:.6f}, btc_var={btc_var:.6f}")
        
        if btc_var == 0:
            logger.warning("Signal computation failed: BTC variance is zero")
            return None

        cov = sum(
            (x - btc_mean) * (y - sol_mean)
            for x, y in zip(self._btc_log, self._sol_log)
        ) / n
        beta = cov / btc_var
        alpha = sol_mean - beta * btc_mean
        logger.debug(f"Pair model: alpha={alpha:.6f}, beta={beta:.6f}, cov={cov:.6f}")

        spread = [
            y - (alpha + beta * x)
            for x, y in zip(self._btc_log, self._sol_log)
        ]
        spread_mean = sum(spread) / n
        spread_var = sum((s - spread_mean) ** 2 for s in spread) / n
        spread_std = math.sqrt(spread_var)
        logger.debug(f"Spread stats: mean={spread_mean:.6f}, var={spread_var:.6f}, std={spread_std:.6f}")
        
        if spread_std == 0:
            logger.warning("Signal computation failed: spread standard deviation is zero")
            return None

        last_spread = spread[-1]
        z_score = (last_spread - spread_mean) / spread_std
        logger.debug(f"Z-score calculation: last_spread={last_spread:.6f}, z_score={z_score:.2f}")

        expected_log_sol = alpha + beta * self._btc_log[-1]
        expected_sol = math.exp(expected_log_sol)
        actual_sol = math.exp(self._sol_log[-1])
        deviation = (actual_sol - expected_sol) / expected_sol
        logger.debug(f"Price prediction: expected_sol={expected_sol:.2f}, actual_sol={actual_sol:.2f}, deviation={deviation:.2%}")

        return z_score, expected_sol, deviation


class SolBtcConvergenceTrader:
    def __init__(self) -> None:
        load_dotenv()
        logger.debug("Environment variables loaded")

        self.trading_client = TradingClient(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
            paper=True,
        )
        logger.info("TradingClient initialized (paper trading mode)")
        
        self.data_stream = CryptoDataStream(
            os.getenv("ALPACA_API_KEY"),
            os.getenv("ALPACA_SECRET_KEY"),
        )
        logger.info("CryptoDataStream initialized")
        
        self.model = RollingPairModel(WINDOW_SIZE)
        self.latest_bars: dict[str, object] = {}
        self.last_processed_time = None
        self.last_trade_time = 0.0
        self.current_bias = "flat"
        
        logger.info(f"Strategy configuration: WINDOW_SIZE={WINDOW_SIZE}, ENTRY_Z={ENTRY_Z}, EXIT_Z={EXIT_Z}, "
                   f"TRADE_NOTIONAL_USD={TRADE_NOTIONAL_USD}, ALLOW_SHORT={ALLOW_SHORT}, "
                   f"MIN_SECONDS_BETWEEN_TRADES={MIN_SECONDS_BETWEEN_TRADES}")

    def _position_qty(self) -> float:
        try:
            position = self.trading_client.get_open_position(SYMBOL_SOL)
        except APIError as e:
            logger.warning(f"APIError while fetching position: {e}")
            return 0.0
        try:
            return float(position.qty)
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to parse position quantity: {e}")
            return 0.0

    def _submit_order(self, side: OrderSide) -> None:
        order = MarketOrderRequest(
            symbol=SYMBOL_SOL,
            notional=TRADE_NOTIONAL_USD,
            side=side,
            time_in_force=TimeInForce.GTC,
        )
        logger.debug(f"Preparing {side.name} market order: symbol={SYMBOL_SOL}, notional={TRADE_NOTIONAL_USD}")
        try:
            self.trading_client.submit_order(order_data=order)
            logger.info(f"Submitted {side.name} market order for {TRADE_NOTIONAL_USD} {SYMBOL_SOL}")
        except Exception as e:
            logger.error(f"Error submitting {side.name} order: {e}", exc_info=True)

    def _close_position(self) -> None:
        try:
            self.trading_client.close_position(SYMBOL_SOL)
            logger.info(f"Closed position in {SYMBOL_SOL}")
        except APIError:
            logger.warning(f"Attempted to close position in {SYMBOL_SOL}, but caught APIError")

    def _apply_trade_decision(self, desired_bias: str) -> None:
        now = time.time()
        time_since_last_trade = now - self.last_trade_time
        logger.debug(f"Trade decision: desired_bias={desired_bias}, current_bias={self.current_bias}, "
                    f"time_since_last_trade={time_since_last_trade:.1f}s")
        
        if now - self.last_trade_time < MIN_SECONDS_BETWEEN_TRADES:
            logger.info(f"Trade blocked by rate limit. {MIN_SECONDS_BETWEEN_TRADES - time_since_last_trade:.1f}s remaining")
            return

        qty = self._position_qty()
        logger.debug(f"Current position quantity: {qty}")
        
        if desired_bias == "flat":
            if qty != 0:
                logger.info(f"Flattening position. Closing position of size {qty}")
                self._close_position()
                self.last_trade_time = now
            self.current_bias = "flat"
            return

        if desired_bias == "short" and not ALLOW_SHORT:
            if qty > 0:
                logger.info("Short signal, but short trading is disabled. Closing long position.")
                self._close_position()
                self.last_trade_time = now
            self.current_bias = "flat"
            return

        if desired_bias == "long":
            if qty <= 0:
                if qty < 0:
                    logger.info("Long signal, but currently short. Closing short before buying.")
                    self._close_position()
                logger.info("Submitting BUY order for LONG entry.")
                self._submit_order(OrderSide.BUY)
                self.last_trade_time = now
            self.current_bias = "long"
            logger.debug(f"Position bias updated to: {self.current_bias}")
            return

        if desired_bias == "short":
            if qty >= 0:
                if qty > 0:
                    logger.info("Short signal, but currently long. Closing long before selling.")
                    self._close_position()
                logger.info("Submitting SELL order for SHORT entry.")
                self._submit_order(OrderSide.SELL)
                self.last_trade_time = now
            self.current_bias = "short"
            logger.debug(f"Position bias updated to: {self.current_bias}")

    async def handle_bar(self, bar) -> None:
        symbol = _bar_symbol(bar)
        logger.debug(f"Received bar for symbol: {symbol}")
        
        if symbol not in {SYMBOL_BTC, SYMBOL_SOL}:
            logger.debug(f"Ignoring bar for symbol {symbol} (not BTC or SOL)")
            return

        self.latest_bars[symbol] = bar
        logger.debug(f"Updated latest_bars: {list(self.latest_bars.keys())}")
        
        if SYMBOL_BTC not in self.latest_bars or SYMBOL_SOL not in self.latest_bars:
            logger.debug("Waiting for both BTC and SOL bars before processing")
            return

        btc_bar = self.latest_bars[SYMBOL_BTC]
        sol_bar = self.latest_bars[SYMBOL_SOL]
        btc_time = _bar_time(btc_bar)
        sol_time = _bar_time(sol_bar)
        
        if btc_time is None or sol_time is None:
            logger.warning("Bar time missing for btc or sol, skipping.")
            return
        
        if btc_time != sol_time:
            logger.debug(f"Bar times not aligned: btc {btc_time}, sol {sol_time}")
            return
        
        if self.last_processed_time == btc_time:
            logger.debug(f"Bar at {btc_time} already processed, skipping")
            return

        self.last_processed_time = btc_time
        btc_close = _bar_close(btc_bar)
        sol_close = _bar_close(sol_bar)
        
        if btc_close is None or sol_close is None:
            logger.warning("Bar close missing for btc or sol, skipping.")
            return

        logger.info(
            f"Bar @ {btc_time} btc={btc_close:.2f} sol={sol_close:.2f}"
        )

        self.model.update(btc_close, sol_close)
        if not self.model.ready():
            logger.debug(f"Model not ready yet (not enough data): {len(self.model._btc_log)}/{WINDOW_SIZE} bars")
            return

        signal = self.model.compute_signal()
        if signal is None:
            logger.debug("Signal computation failed, skipping.")
            return

        z_score, expected_sol, deviation = signal
        logger.info(
            f"z={z_score:.2f} expected_sol={expected_sol:.2f} "
            f"dev={deviation:.2%} sol={sol_close:.2f}"
        )

        desired_bias = self.current_bias
        if z_score >= ENTRY_Z:
            desired_bias = "short"
            logger.debug(f"Z-score {z_score:.2f} >= ENTRY_Z {ENTRY_Z}, setting bias to short")
        elif z_score <= -ENTRY_Z:
            desired_bias = "long"
            logger.debug(f"Z-score {z_score:.2f} <= -ENTRY_Z {-ENTRY_Z}, setting bias to long")
        elif abs(z_score) <= EXIT_Z:
            desired_bias = "flat"
            logger.debug(f"|Z-score| {abs(z_score):.2f} <= EXIT_Z {EXIT_Z}, setting bias to flat")
        else:
            logger.debug(f"Z-score {z_score:.2f} in neutral zone, keeping bias {desired_bias}")

        if desired_bias != self.current_bias:
            logger.info(f"Signal change: {self.current_bias} -> {desired_bias} (z_score={z_score:.2f})")
            self._apply_trade_decision(desired_bias)
        else:
            logger.debug(f"No bias change needed: {self.current_bias} (z_score={z_score:.2f})")

    def run(self) -> None:
        logger.info(f"Subscribing to bars for {SYMBOL_BTC}, {SYMBOL_SOL}")
        self.data_stream.subscribe_bars(self.handle_bar, SYMBOL_BTC, SYMBOL_SOL)
        logger.info(f"Successfully subscribed to bars for {SYMBOL_BTC} and {SYMBOL_SOL}")
        logger.info("Starting crypto data stream event loop")
        try:
            self.data_stream.run()
        except Exception as e:
            logger.error(f"Error in data stream: {e}", exc_info=True)
            raise


def main() -> None:
    trader = SolBtcConvergenceTrader()
    trader.run()


if __name__ == "__main__":
    logger.info('Starting sol btc strategy ...')
    main()
