import gym
from gym.spaces import Discrete, Box
from gym.envs.registration import register
import numpy as np

from stock_data import generate_prices, training_episode, testing_episode


class RandMarketEnvGym(gym.Env):
    """
    Rand market env for single agent
    """
    metadata = {
        'render_modes': ['human']
    }

    def __init__(self, render_mode=None):
        self.action_space = Discrete(3)
        self.observation_space = Box(low=0, high=1000000000, shape=(102,), dtype=np.float64)

        self.day = 0

        self.DATA = generate_prices()
        
        self.history = self.DATA[self.day: self.day + 100]

        assert render_mode in self.metadata['render_modes'] or render_mode is None
        self.render_mode = render_mode

        self._action_meanings = {
            0: 'BUY',
            1: 'HOLD',
            2: 'SELL',
        }

        self.cash = 1000
        self.assets = 0
    
    def _get_obs(self):
        obs = np.array(self.history + [self.cash, self.assets])
        assert obs.shape == (102,)
        return obs

    def _get_info(self):
        return {
            'cash': self.cash,
            'assets': self.assets,
            'value': self.cash + self.assets * self.history[-1],
            'start': self.DATA[100],
            'end': self.DATA[-1],
        }

    def reset(self):
        self.day = 0

        self.DATA = generate_prices()

        self.history = self.DATA[self.day: self.day + 100]

        self.cash = 1000
        self.assets = 0

        if self.render_mode == 'human':
            print(self._get_info())

        return self._get_obs(), self._get_info()
    
    def step(self, action):
        assert self.action_space.contains(action)

        if action == 0:
            self.assets += 1
            self.cash -= self.history[-1]
        elif action == 2:
            self.assets -= 1
            self.cash += self.history[-1]
        
        self.day += 1
        self.history = self.DATA[self.day: self.day + 100]

        terminated = self.day >= 900
        reward = self._get_info()['value']
        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == 'human':
            print(info)
        
        return obs, reward, terminated, False, info
    
    def close(self):
        pass


class RealMarketEnvGym(gym.Env):
    """
    Real market env for single agent
    """
    metadata = {
        'render_modes': ['human']
    }

    def __init__(self, render_mode=None):
        self.action_space = Discrete(3)
        self.observation_space = Box(low=0, high=1000000000, shape=(102,), dtype=np.float64)

        self.day = 0

        self.DATA = training_episode()
        
        self.history = self.DATA[self.day: self.day + 100]

        assert render_mode in self.metadata['render_modes'] or render_mode is None
        self.render_mode = render_mode

        self._action_meanings = {
            0: 'BUY',
            1: 'HOLD',
            2: 'SELL',
        }

        self.cash = 1000
        self.assets = 0
    
    def _get_obs(self):
        obs = np.array(self.history + [self.cash, self.assets])
        assert obs.shape == (102,)
        return obs

    def _get_info(self):
        return {
            'cash': self.cash,
            'assets': self.assets,
            'value': self.cash + self.assets * self.history[-1],
            'start': self.DATA[100],
            'end': self.DATA[-1],
        }

    def reset(self, training=True):
        self.day = 0

        if training:
            self.DATA = training_episode()
        else:
            self.DATA = testing_episode()

        self.history = self.DATA[self.day: self.day + 100]

        self.cash = 1000
        self.assets = 0

        if self.render_mode == 'human':
            print(self._get_info())

        return self._get_obs(), self._get_info()
    
    def step(self, action):
        assert self.action_space.contains(action)

        if action == 0:
            self.assets += 10 / self.history[-1]
            self.cash -= 10
        elif action == 2:
            self.assets -= 10 / self.history[-1]
            self.cash += 10
        
        self.day += 1
        self.history = self.DATA[self.day: self.day + 100]

        terminated = self.day >= 100
        reward = self._get_info()['value']
        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == 'human':
            print(info)
        
        return obs, reward, terminated, False, info
    
    def close(self):
        pass


register(
    id='rand_market_env_gym-v0',
    max_episode_steps=500,
    entry_point='market.rl.real_market_env_gym:RandMarketEnvGym',
)

register(
    id='real_market_env_gym-v0',
    max_episode_steps=100,
    entry_point='market.rl.real_market_env_gym:RealMarketEnvGym',
)






