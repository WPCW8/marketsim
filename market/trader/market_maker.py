from numpy import random
from decimal import Decimal

from market.exchange.exchange import Exchange
from market.order.order import Order
from market.trader.trader import Trader

from typing import Union

class MarketMaker(Trader):

    def __init__(self, name: str, trader_id: str, volume: int = 1, variance: float = 0.3) -> None:
        super().__init__(name, trader_id, Decimal(10000), Decimal(100), 'Market maker')
        self.volume = volume
        self.variance = variance

    def decide(self, exchange: Exchange) -> Union[Order, None]:
        bid, ask = exchange.orderbook.best_bid(), exchange.orderbook.best_ask()
        if bid is None:
            bid = Decimal(100.001)
        else:
            bid = bid[0]
        if ask is None:
            ask = Decimal(99.999)
        else:
            ask = ask[0]

        if random.random() < 0.5:
            price = Decimal(random.normal(bid, self.variance)).quantize(Decimal('0.000001'))
            return Order(price, Decimal(max(random.normal(self.volume, 0.5), 0)), self.id)
        price = Decimal(random.normal(ask, self.variance)).quantize(Decimal('0.000001'))
        return Order(price, Decimal(-max(random.normal(self.volume, 0.5), 0)), self.id)
