from market.exchange.exchangeorderbook import ExchangeOrderBook
from decimal import Decimal

from tqdm import tqdm

from market.order.order import Order
from market.trader.trader import Trader

from collections import deque


class Exchange:
    """
    An exchange is a market where traders can buy and sell assets.
    """

    def __init__(self, name: str, traders: list[Trader],
                 log_file: str = '/Users/varun/Library/Mobile Documents/com~apple~CloudDocs/fyp2/tmp/log.csv') -> None:
        self.name = name
        self.traders: dict[str: Trader] = {}
        for trader in traders:
            self.traders[trader.id] = trader

        self.orderbook = ExchangeOrderBook()
        self.daily_prices: dict[str: float] = {
            'volume': 0
        }

        self.log_file = log_file
        with open(log_file, 'w') as f:
            f.write('time,open,high,low,close,volume\n')

        self.recent_history = deque([100] * 100, maxlen=100)
        self.time = 0

        self.trades = 0

    def log_day(self):
        _open = self.daily_prices['open'] if 'open' in self.daily_prices else 'null'
        high = self.daily_prices['high'] if 'high' in self.daily_prices else 'null'
        low = self.daily_prices['low'] if 'low' in self.daily_prices else 'null'
        close = self.daily_prices['close'] if 'close' in self.daily_prices else 'null'
        volume = self.daily_prices['volume'] if 'volume' in self.daily_prices else 'null'

        if close != 'null':
            self.recent_history.append(close)
        elif close == 'null' and len(self.recent_history) > 0:
            self.recent_history.append(self.recent_history[-1])

        with open(self.log_file, 'a') as f:
            f.write(f'{self.time},{_open},{high},{low},{close},{volume}\n')

    def log_order_fulfilled(self, quantity: Decimal, price: Decimal) -> None:
        """
        Log a message about an order being fulfilled.

        :param quantity: The quantity that was traded
        :param price: The price that was traded at
        """
        self.daily_prices['close'] = price
        if 'open' not in self.daily_prices:
            self.daily_prices['open'] = price

        if 'high' not in self.daily_prices or price > self.daily_prices['high']:
            self.daily_prices['high'] = price

        if 'low' not in self.daily_prices or price < self.daily_prices['low']:
            self.daily_prices['low'] = price

        self.daily_prices['volume'] += quantity

    def log_order_received(self, quantity: Decimal, price: Decimal, trader: Trader) -> None:
        """
        Log a message about an order being rejected.

        :param quantity: The quantity that was traded
        :param price: The price that was traded at
        :param trader: The trader that fulfilled the order
        """
        pass

    def run(self, duration: int, progress_bar=False) -> None:
        """
        Run the exchange for a given duration.

        :param duration: The duration to run the exchange for
        :param progress_bar: Whether to show a progress bar
        :return: None
        """
        wrapper = tqdm if progress_bar else lambda x: x
        for _ in wrapper(range(duration)):
            for trader in self.traders.values():
                order = trader.decide(self)
                if order is not None:
                    self.add_order(order)
            self.log_day()
            self.daily_prices: dict[str: float or None] = {
                'volume': Decimal(0)
            }
            self.time += 1

    def add_order(self, order: Order) -> None:
        """
        Add a list of orders to the exchange.

        :param order: The order to add
        :return: None
        """
        bid = order.quantity > 0
        if bid:
            self.add_bid(order.price, order.quantity, order.trader_id)
        else:
            self.add_ask(order.price, -order.quantity, order.trader_id)

    def add_bid(self, price: Decimal, quantity: Decimal, trader_id: str):
        self.orderbook.insert_bid(price, quantity, trader_id)
        self.match_orders()

    def add_ask(self, price: Decimal, quantity: Decimal, trader_id: str):
        self.orderbook.insert_ask(price, quantity, trader_id)
        self.match_orders()

    def match_orders(self):
        best_bid = self.orderbook.best_bid()
        best_ask = self.orderbook.best_ask()
        while best_bid is not None and best_ask is not None and best_bid[0] >= best_ask[0]:
            quantity = min(best_bid[1], best_ask[1])

            buyer, seller = self.orderbook.match(best_bid[0], best_ask[0], quantity)
            self.traders[buyer].assets += quantity
            self.traders[buyer].cash -= quantity * best_ask[0]
            self.traders[seller].assets -= quantity
            self.traders[seller].cash += quantity * best_ask[0]

            self.log_order_fulfilled(quantity, best_ask[0])
            self.trades += 1

            best_bid = self.orderbook.best_bid()
            best_ask = self.orderbook.best_ask()
