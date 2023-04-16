import functools

import gymnasium
import numpy as np
from gymnasium.spaces import Discrete

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.test import api_test

from stock_data import generate_prices

from utils import agent_selector


def env(render_mode=None, **kwargs):
    env = raw_env(render_mode=render_mode, **kwargs)
    # env = wrappers.AssertOutOfBoundsWrapper(env)
    # env = wrappers.NanNoOpWrapper(env, 0)
    # env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    def __init__(self, render_mode=None, num_agents=2, influence_factor=0.1):
        super().__init__()
        self.possible_agents = [f'agent_{i}' for i in range(num_agents)]
        self._action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        self._observation_spaces = {
            agent: gymnasium.spaces.Box(low=0, high=1000000000, shape=(102,), dtype=np.float64)
            for agent in self.possible_agents
        }
        self.render_mode = render_mode

        self.data = generate_prices(n=100)

        self.price = 100
        self.net_volume = 0
        self.day = 0

        self.influence_factor = influence_factor

        self.cash = {agent: 1000 for agent in self.possible_agents}
        self.assets = {agent: 0 for agent in self.possible_agents}

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent) -> gymnasium.spaces.Space:
        return self._observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent) -> gymnasium.spaces.Space:
        return self._action_spaces[agent]
    
    def render(self, mode='human'):
        pass

    def _get_obs(self, agent):
        obs = np.array(self.data[-100:] + [self.cash[agent], self.assets[agent]])
        assert obs.shape == (102,)
        return obs

    def observe(self, agent):
        return self._get_obs(agent)
    
    def close(self):
        pass

    def reset(self, seed=None, options=None, **kwargs):
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: 1 for agent in self.agents}
        self.observations = {agent: self.observe(agent) for agent in self.agents}

        self.data = generate_prices(n=100)

        self.price = 100
        self.day = 0
        self.cash = {agent: 1000 for agent in self.possible_agents}
        self.assets = {agent: 0 for agent in self.possible_agents}
        
        self.agent_selector = agent_selector(self.possible_agents, reorder=True)
        self.agent_selection = self.agent_selector.next()
    
    def step(self, action) -> None:
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            self._was_dead_step(action)
            return
        
        assert self.action_space(self.agent_selection).contains(action)

        if action == 0 and self.cash[self.agent_selection] >= 10:
            self.cash[self.agent_selection] -= 10
            self.assets[self.agent_selection] += 10 / self.price
            self.net_volume += 10
        elif action == 2 and self.assets[self.agent_selection] >= 10 / self.price:
            self.cash[self.agent_selection] += 10
            self.assets[self.agent_selection] -= 10 / self.price
            self.net_volume -= 10
        self.state[self.agent_selection] = action
        

        if self.agent_selector.is_last():
            self.day += 1
            self.price = np.random.normal(self.price + self.influence_factor * self.net_volume, 1)
            self.data.append(self.price)

            self.net_volume = 0

            self.terminations = {agent: self.day >= 100 for agent in self.agents}
            self.truncations = {agent: False for agent in self.agents}
            self.infos = {agent: {} for agent in self.agents}
            self.observations = {agent: self.observe(agent) for agent in self.agents}
        else:
            self._cumulative_rewards[self.agent_selection] = round(self.cash[self.agent_selection] + self.assets[self.agent_selection] * self.price, 5)
            self.rewards[self.agent_selection] = round(self.cash[self.agent_selection] + self.assets[self.agent_selection] * self.price, 5)

            self.terminations = {agent: False for agent in self.agents}
            self.truncations = {agent: False for agent in self.agents}
            self.infos = {agent: {} for agent in self.agents}
            self.observations = {agent: self.observe(agent) for agent in self.agents}
        
        self.agent_selection = self.agent_selector.next()

if __name__ == '__main__':
    e = env()
    api_test(e, num_cycles=1000, verbose_progress=True)



        


    


    

