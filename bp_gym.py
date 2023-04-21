import gymnasium as gym
from gymnasium import spaces
import util
from bppy import BProgram
from bp_wrapper import BPwrapper
from strategy_bthreads import create_strategies, number_of_bthreads, bthreads_progress
from priority_event_selection_strategy import PriorityEventSelectionStrategy
import numpy as np

class BPGymEnv(gym.Env):
    def __init__(self, env):
        self.env = env
        
        self.action_space = env.action_space

        # bthreads observation space is a box with number of bthreads with each value between -inf and inf, and should be integer
        bthreads_obs_space = spaces.Box(shape=(number_of_bthreads(),), low=-np.infty, high=np.infty, dtype=np.int32)
        observation_space = spaces.Tuple((env.observation_space, bthreads_obs_space))
        self.observation_space = observation_space

        # initialize the bprogram containing the strategies
        if (util.ADD_STRATEGIES):
            self.bprog = BPwrapper()
            bprogram = BProgram(bthreads=create_strategies(), event_selection_strategy=PriorityEventSelectionStrategy())
            self.bprog.reset(bprogram)


    def step(self, action):
        observation, reward, done, info = self.env.step(action)

        if (util.ADD_STRATEGIES):
            # advance the bprogram
            self.bprog.advance_randomly()
            observation = (observation, self._get_strategies_progress())

        return observation, reward, done, info 
    
    def reset(self):
        return self.env.reset()
    
    def render(self, mode='human'):
        return self.env.render(mode)
    
    def close(self):
        return self.env.close()

    def _get_strategies_progress(self):
        return list(bthreads_progress.values())