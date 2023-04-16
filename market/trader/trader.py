from decimal import Decimal
from market.order.order import Order

from typing import Union


class Trader:
    def __init__(self, name: str, trader_id: str,
                 initial_cash: Decimal = Decimal(1000), initial_assets: Decimal = Decimal(100),
                 trader_type: str = '') -> None:
        """
        A trader trades on an exchange.
        Please subclass this class to implement your own trading strategy.

        :param name: Name of the trader
        :param trader_id: Unique id of the trader
        """
        self.name = name
        self.id = trader_id
        self.trader_type = trader_type

        self.initial_cash = initial_cash
        self.initial_assets = initial_assets

        self.cash = initial_cash
        self.assets = initial_assets

    def set_cash(self, cash: Decimal):
        """
        Set the amount of cash the trader has. DEBUG ONLY.

        :param cash: Amount of cash
        """
        self.cash = cash

    def set_assets(self, quantity: Decimal):
        """
        Set the amount of assets the trader has. DEBUG ONLY.

        :param quantity: Amount of asset
        """
        self.assets = quantity

    def decide(self, exchange: 'Exchange') -> Union[Order, None]:
        """
        Decide what to do on the exchange. This method is called by the exchange every time step.
        Use this method to develop your trading strategy.

        :param exchange: The exchange
        """
        raise NotImplementedError("This method must be implemented by a subclass")

    def __repr__(self):
        return self.name

    def __hash__(self):
        """
        DO NOT OVERRIDE THIS METHOD. This method is used to identify traders.

        :return: None
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        DO NOT OVERRIDE THIS METHOD. This method is used to identify traders.

        :return: None
        """
        return self.id == other.id

    def __lt__(self, other):
        """
        DO NOT OVERRIDE THIS METHOD. This method is used to sort traders.

        :return: None
        """
        return self.id < other.id


