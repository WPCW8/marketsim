"""
TODO Use petting zoo to create a custom environment for the market
TODO Use pytorch for the agent models
TODO Train the agent with a jupyter notebook
"""

import functools
from copy import copy
from decimal import Decimal

import numpy as np
from pettingzoo.utils.env import ParallelEnv
from gymnasium.spaces import Box

from market.exchange.exchange import Exchange
from market.trader.trader import Trader
from market.order.order import Order


class RLTrader(Trader):
    def __init__(self, name: str, trader_id: str) -> None:
        super().__init__(name, trader_id, Decimal(0), Decimal(100), 'RL Trader')

    def decide(self, exchange: Exchange):
        pass


class ExchangeEnv(ParallelEnv):
    def __init__(self, num_traders: int, exchange_name: str = 'ExchangeEnv'):
        self.num_traders = num_traders
        self.possible_agents = [f'trader_{i}' for i in range(num_traders)]

        self.traders = [RLTrader(f'Trader {i}', f'trader_{i}') for i in range(num_traders)]
        self.exchange = Exchange(exchange_name, self.traders)

        self.timestep = None

    def get_agent_observation(self, agent):
        history = list(self.exchange.recent_history)
        if len(history) > 100:
            history = history[-100:]
        elif len(history) < 100:
            history = [0] * (100 - len(history)) + history

        return (
            *history,
            float(self.traders[int(agent.split('_')[1])].cash),
            float(self.traders[int(agent.split('_')[1])].assets)
        )

    def reset(self, seed=None, return_info=False, options=None):
        self.agents = copy(self.possible_agents)
        self.timestep = 0

        self.traders = [RLTrader(f'Trader {i}', f'trader_{i}') for i in range(self.num_traders)]
        self.exchange = Exchange(self.exchange.name, self.traders)

        return {
            agent: self.get_agent_observation(agent) for agent in self.agents
        }

    def get_agent_reward(self, agent):
        if self.exchange.recent_history:
            return self.traders[int(agent.split('_')[1])].cash + self.traders[int(agent.split('_')[1])].assets * \
                   self.exchange.recent_history[-1]
        return self.traders[int(agent.split('_')[1])].cash

    def step(self, actions):
        for agent, action in actions.items():
            def decide(_):
                return Order(Decimal(float(action[0])), Decimal(float(action[1])), agent)

            self.exchange.traders[agent].decide = decide

        self.exchange.run(1)
        self.timestep += 1

        # observation, reward, termination, truncation, info
        return {
                   agent: self.get_agent_observation(agent)
                   for agent in self.agents
               }, {
                   agent: self.get_agent_reward(agent)
                   for agent in self.agents
               }, {
                   agent: False
                   for agent in self.agents
               }, {
                   agent: False
                   for agent in self.agents
               }, {
                   agent: {}
                   for agent in self.agents
               }

    def render(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=np.array([0] * 100 + [0, 0]),
                   high=np.array([1_000_000] * 100 + [1_000_000, 1_000_000], dtype=np.float32))

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Box(low=np.array([0, -10]), high=np.array([1_000_000, 10]), dtype=np.float32)

    def seed(self, seed=None):
        super().seed(seed)

    def state(self) -> np.ndarray:
        return super().state()


from pettingzoo.test import parallel_api_test  # noqa: E402

if __name__ == '__main__':
    parallel_api_test(ExchangeEnv(4), num_cycles=400)
