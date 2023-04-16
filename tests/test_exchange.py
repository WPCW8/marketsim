from market.exchange.exchange import Exchange
from market.order.order import Order
from market.trader.market_maker import MarketMaker

from market.exchange.exchangeorderbook import ExchangeOrderBook


class TestOrderbook:
    def test_bid(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(100, 10, 't1')
        assert ob.best_bid() == [100, 10]
    
    def test_ask(self):
        ob = ExchangeOrderBook()
        ob.insert_ask(100, 10, 't1')
        assert ob.best_ask() == [100, 10]
    
    def test_match(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(100, 10, 't1')
        ob.insert_ask(100, 10, 't2')
        assert ob.match(100, 100, 10) == ('t1', 't2')
        assert ob.best_bid() is None
        assert ob.best_ask() is None
    
    def test_match1_5(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(10, 10, 't1')
        ob.insert_ask(9, 5, 't2')
        assert ob.match(10, 9, 5) == ('t1', 't2')
        assert ob.best_bid() == [10, 5]
        assert ob.best_ask() is None
    
    def test_match2(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(100, 10, 't1')
        ob.insert_ask(100, 5, 't2')
        ob.insert_ask(100, 5, 't3')
        assert ob.match(100, 100, 5) == ('t1', 't2')
        assert ob.match(100, 100, 5) == ('t1', 't3')
        assert ob.best_bid() is None
        assert ob.best_ask() is None
    
    def test_match3(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(100, 5, 't1')
        ob.insert_bid(100, 5, 't2')
        ob.insert_ask(100, 10, 't3')
        assert ob.match(100, 100, 5) == ('t1', 't3')
        assert ob.match(100, 100, 5) == ('t2', 't3')
        assert ob.best_bid() is None
        assert ob.best_ask() is None
    
    def test_l2(self):
        ob = ExchangeOrderBook()
        ob.insert_bid(100, 10, 't1')
        ob.insert_ask(100, 10, 't2')
        assert ob.to_l2_dict() == {
            'bids': {100: 10},
            'asks': {100: 10}
        }


class TestExchange:
    def test_start(self):
        e = Exchange('Exchange', [MarketMaker('mm0', 'mm0'), MarketMaker('mm1', 'mm1')])
        assert e.time == 0

    def test_run(self):
        e = Exchange('Exchange', [MarketMaker('mm0', 'mm0'), MarketMaker('mm1', 'mm1')])
        e.run(100)
        assert e.time == 100
    



