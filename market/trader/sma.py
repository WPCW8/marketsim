from decimal import Decimal

from market.exchange.exchange import Exchange
from market.order.order import Order
from market.trader.trader import Trader

from typing import Union


class SMATrader(Trader):
    def __init__(self, name: str, trader_id: str, short_window: int = 10, long_window: int = 50) -> None:
        super().__init__(name, trader_id, Decimal(1000), Decimal(100), f'SMA Trader ({short_window}, {long_window})')
        self.short_window = short_window
        self.long_window = long_window
        self.short_sma = None
        self.long_sma = None

    def decide(self, exchange: Exchange) -> Union[Order, None]:
        prices = list(exchange.recent_history)[-self.long_window:]
        if len(prices) < self.long_window:
            return None
        long_sma = sum(prices[-self.long_window:]) / self.long_window
        short_sma = sum(prices[-self.short_window:]) / self.short_window
        if short_sma > long_sma:
            return Order(prices[-1], Decimal(1), self.id)
        elif short_sma < long_sma:
            return Order(prices[-1], Decimal(-1), self.id)
        return None
