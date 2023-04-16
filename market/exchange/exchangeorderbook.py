from order_book import OrderBook
from decimal import Decimal


class L3OrderSignature:
    def __init__(self, quantity: Decimal, trader_id: str):
        self.quantity = quantity
        self.trader_id = trader_id

    def __repr__(self):
        return f'({self.quantity}, {self.trader_id})'


class ExchangeOrderBook:
    def __init__(self):
        self.l3 = OrderBook()

    def insert_bid(self, price: Decimal, quantity: Decimal, trader: str):
        if price not in self.l3.bids:
            self.l3.bids[price] = [L3OrderSignature(quantity, trader)]
        else:
            self.l3.bids[price].append(L3OrderSignature(quantity, trader))

    def insert_ask(self, price: Decimal, quantity: Decimal, trader: str):
        if price not in self.l3.asks:
            self.l3.asks[price] = [L3OrderSignature(quantity, trader)]
        else:
            self.l3.asks[price].append(L3OrderSignature(quantity, trader))

    def match(self, bid_price: Decimal, ask_price: Decimal, quantity: Decimal) -> tuple[str, str]:
        if bid_price not in self.l3.bids or ask_price not in self.l3.asks:
            print(bid_price, ask_price, quantity)
            raise ValueError('Invalid bid or ask price')

        if self.l3.bids[bid_price][0].quantity > self.l3.asks[ask_price][0].quantity:
            self.l3.bids[bid_price][0].quantity -= self.l3.asks[ask_price][0].quantity
            buyer, seller = self.l3.bids[bid_price][0].trader_id, self.l3.asks[ask_price][0].trader_id
            self.l3.asks[ask_price].pop(0)
            if len(self.l3.asks[ask_price]) == 0:
                del self.l3.asks[ask_price]
        elif self.l3.bids[bid_price][0].quantity < self.l3.asks[ask_price][0].quantity:
            self.l3.asks[ask_price][0].quantity -= self.l3.bids[bid_price][0].quantity
            buyer, seller = self.l3.bids[bid_price][0].trader_id, self.l3.asks[ask_price][0].trader_id
            self.l3.bids[bid_price].pop(0)
            if len(self.l3.bids[bid_price]) == 0:
                del self.l3.bids[bid_price]
        else:
            buyer, seller = self.l3.bids[bid_price][0].trader_id, self.l3.asks[ask_price][0].trader_id
            self.l3.bids[bid_price].pop(0)
            self.l3.asks[ask_price].pop(0)
            if len(self.l3.bids[bid_price]) == 0:
                del self.l3.bids[bid_price]
            if len(self.l3.asks[ask_price]) == 0:
                del self.l3.asks[ask_price]

        return buyer, seller

    def to_l2_dict(self):
        return {
            'bids': {k: sum([x.quantity for x in v]) for k, v in self.l3.bids.to_dict().items()},
            'asks': {k: sum([x.quantity for x in v]) for k, v in self.l3.asks.to_dict().items()}
        }

    def best_bid(self) -> tuple[Decimal, Decimal] or None:
        try:
            l = self.l3.bids.index(0)
            return [l[0], sum([x.quantity for x in l[1]])]
        except IndexError:
            return None

    def best_ask(self) -> tuple[Decimal, Decimal] or None:
        try:
            l = self.l3.asks.index(0)
            return [l[0], sum([x.quantity for x in l[1]])]
        except IndexError:
            return None
