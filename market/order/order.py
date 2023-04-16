from decimal import Decimal


class Order:
    def __init__(self, price: Decimal, quantity: Decimal, trader_id: str):
        """
        An order to buy or sell.

        :param price: The price to buy or sell at (per unit)
        :param quantity: The quantity to buy or sell (negative for sell)
        :param trader_id: The trader who placed the order
        """
        self.price = price
        self.quantity = quantity
        self.trader_id = trader_id

    def __repr__(self):
        return f'Order({self.price}, {self.quantity}, {self.trader_id})'
