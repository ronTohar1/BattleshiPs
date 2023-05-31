import gymnasium
from gymnasium import spaces
from bppy import BProgram
from bp_wrapper import BPwrapper
from strategy_bthreads import create_strategies, number_of_bthreads, bthreads_progress, reset_all_strategies, set_state
# from priority_event_selection_strategy import PriorityEventSelectionStrategy
import numpy as np
from bppy import *
from util import BOARD_SIZE
from virtual_block_ess import VirtualBlockEventSelectionStrategy

class BPGymEnv(gymnasium.Env):
    def __init__(self, env, add_strategies=False): # Expecting an environment with a gymnasium interface
        self.add_strategies = add_strategies
        self.env = env
        self.action_space = env.action_space
        self.observation_space = env.observation_space

        # initialize the bprogram containing the strategies
        if (self.add_strategies):
            channels = env.observation_space.shape[0]
            observation_space = spaces.Box(shape=(number_of_bthreads() + channels, BOARD_SIZE, BOARD_SIZE), low=0, high=1, dtype=np.float32)
            self.observation_space = observation_space
            self.bprog = BPwrapper()


    def _get_tuple_action(self, action):
        if isinstance(action, str):
            action = eval(action) # should convert to int or tuple
        if isinstance(action, np.int32) or isinstance(action, np.int64) or isinstance(action, int):
            return (action % BOARD_SIZE, action // BOARD_SIZE)
        if not isinstance(action, tuple):
            raise Exception("Action must be tuple or int, real type - ", type(action))
        return action

    # Concatenate the observations from the environment and the strategies
    # env_obs - the observation from the environment (numpy array of 2 - 10x10 boards)
    # bp_obs - the observation from the strategies (numpy array of x - 10x10 boards)
    def _concat_observations(self, env_obs, bp_obs):
        return np.concatenate((env_obs, bp_obs), axis=0)

    def step(self, action):
        observation, reward, terminated, truncated, info = self.env.step(action)
        set_state(observation)
        
        if (self.add_strategies):
            # advance the bprogram
            self.bprog.choose_event(BEvent(str(self._get_tuple_action(action))))
            bp_obs = self._get_bp_observation()
            observation = self._concat_observations(observation, bp_obs)
            # print("Observation",observation)
    
        return observation, reward, terminated, truncated, info 
    
    
    def reset(self,seed=None, options=None):

        observation, info = self.env.reset()
        set_state(observation)

        if (self.add_strategies):
            self._reset_strategies()
            obs_strats = self._get_bp_observation()
            observation = self._concat_observations(observation, obs_strats)
            # print("reset observation:",observation)

        return observation, info
    
    def render(self):
        return self.env.render()
    
    def close(self):
        return self.env.close()

    def _get_bp_observation(self):
        strategies = bthreads_progress.values()
        return np.array([np.array(strategy) for strategy in strategies])
    
    def _reset_strategies(self):
        bprogram = BProgram(bthreads=create_strategies(), event_selection_strategy=VirtualBlockEventSelectionStrategy())
        self.bprog.reset(bprogram)
        reset_all_strategies()