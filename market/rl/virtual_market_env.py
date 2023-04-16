import functools

import gymnasium
import numpy as np
from gymnasium.spaces import Discrete

from pettingzoo import AECEnv
from pettingzoo.test import api_test
from utils import agent_selector

import order_book as ob


class L3OrderBook:
    def __init__(self):
        self.ob = ob.OrderBook()
    
    def add_bid(self, price, volume, agent):
        if price in self.ob.bids:
            self.ob.bids[price].append((volume, agent))
        else:
            self.ob.bids[price] = [(volume, agent)]
    
    def add_ask(self, price, volume, agent):
        if price in self.ob.asks:
            self.ob.asks[price].append((volume, agent))
        else:
            self.ob.asks[price] = [(volume, agent)]
    
    def best_ask(self):
        best_ask_price, best_ask_order = self.ob.asks.index(0)
        return best_ask_price, best_ask_order[0]
    
    def best_bid(self):
        best_bid_price, best_bid_order = self.ob.bids.index(0)
        return best_bid_price, best_bid_order[0]
    
    def next_matched_order(self):
        try:
            best_bid_price, best_bid_order = self.best_bid()
        except IndexError:
            return None, None, None, None
        
        try:
            best_ask_price, best_ask_order = self.best_ask()
        except IndexError:
            return None, None, None, None
    
        if best_bid_price >= best_ask_price:
            return best_bid_price, best_bid_order, best_ask_price, best_ask_order
        return None, None, None, None


def env(render_mode=None):
    return raw_env()


class raw_env(AECEnv):
    def __init__(self, num_traders=4):
        self.num_traders = num_traders
        self.agents = ["agent_" + str(i) for i in range(num_traders)]
        self.possible_agents = self.agents[:]

        self._action_spaces = {agent: Discrete(3) for agent in self.agents}
        self._observation_spaces = {
            agent: gymnasium.spaces.Box(low=0, high=1000000000, shape=(102,), dtype=np.float64)
            for agent in self.agents
        }

        self.order_book = L3OrderBook()
        self.prices = [10] * 100

        self.cash = {agent: 1000 for agent in self.agents}
        self.assets = {agent: 100 for agent in self.agents}

        self.day = 0
        self.net_volume = 0

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
    
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent) -> gymnasium.spaces.Space:
        return self._observation_spaces[agent]
    
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent) -> gymnasium.spaces.Space:
        return self._action_spaces[agent]
    
    def observe(self, agent: str):
        return np.array(self.prices[-100:] + [self.cash[agent], self.assets[agent]]).astype(np.float64)

    def reset(self, seed=None, options=None, **kwargs):
        self.agents = self.possible_agents[:]

        self.prices = [10] * 100
        self.order_book = L3OrderBook()

        self.cash = {agent: 1000 for agent in self.agents}
        self.assets = {agent: 100 for agent in self.agents}

        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: 1 for agent in self.agents}
        self.observations = {agent: self.observe(agent) for agent in self.agents}

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

        self.day = 0
    
    def get_last_price(self):
        if len(self.prices) == 0:
            return 10
        return self.prices[-1]
    
    def step(self, action):
        agent = self.agent_selection

        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return

        if action == 0 and self.cash[agent] >= 10:
            self.cash[agent] -= 10
            self.order_book.add_bid(self.get_last_price(), 10, agent)
        elif action == 1 and self.assets[agent] >= 10:
            self.assets[agent] -= 10
            self.order_book.add_ask(self.get_last_price(), 10, agent)
        self.state[agent] = action

        bid_price, bid_order, ask_price, ask_order = self.order_book.next_matched_order()
        if bid_price is not None:
            v1, buyer = bid_order
            v2, seller = ask_order
            volume = min(v1, v2)
            self.cash[buyer] -= volume * ask_price
            self.cash[seller] += volume * ask_price
            self.assets[buyer] += volume
            self.assets[seller] -= volume
            self.net_volume += volume

            if v2 == volume == v1:
                self.order_book.ob.bids[bid_price].pop(0)
                self.order_book.ob.asks[ask_price].pop(0)
            elif v2 == volume:
                self.order_book.ob.bids[bid_price][0] = (v1 - volume, buyer)
                self.order_book.ob.asks[ask_price].pop(0)
            else:
                self.order_book.ob.asks[ask_price][0] = (v2 - volume, seller)
                self.order_book.ob.bids[bid_price].pop(0)

        if self._agent_selector.is_last():
            self.day += 1
            self.price = np.random.normal(self.price + self.influence_factor * self.net_volume, 1)
            self.data.append(self.price)

            self.net_volume = 0

            self.terminations = {agent: self.day >= 100 for agent in self.agents}
            self.truncations = {agent: False for agent in self.agents}
            self.infos = {agent: {} for agent in self.agents}
            self.observations = {agent: self.observe(agent) for agent in self.agents}
        else:
            # self._cumulative_rewards[self.agent_selection] = round(self.cash[self.agent_selection] + self.assets[self.agent_selection] * self.price, 5)
            # self.rewards[self.agent_selection] = round(self.cash[self.agent_selection] + self.assets[self.agent_selection] * self.price, 5)

            self.terminations = {agent: False for agent in self.agents}
            self.truncations = {agent: False for agent in self.agents}
            self.infos = {agent: {} for agent in self.agents}
            self.observations = {agent: self.observe(agent) for agent in self.agents}


if __name__ == '__main__':
    e = env()
    api_test(e, num_cycles=1000, verbose_progress=True)

