import gymnasium
from gymnasium import spaces
from bppy import BProgram
from bp_wrapper import BPwrapper
from strategy_bthreads import create_strategies, number_of_bthreads, bthreads_progress, reset_all_progress, set_state
# from priority_event_selection_strategy import PriorityEventSelectionStrategy
import numpy as np
from bppy import *
from util import BOARD_SIZE

class BPGymEnv(gymnasium.Env):
    def __init__(self, env, add_strategies=False): # Expecting an environment with a gymnasium interface
        self.add_strategies = add_strategies
        self.env = env
        self.action_space = env.action_space
        self.observation_space = env.observation_space

        # initialize the bprogram containing the strategies
        if (self.add_strategies):
            # bthreads observation space is a box with number of bthreads with each value between -inf and inf, and should be integer
            bthreads_obs_space = spaces.Box(shape=(number_of_bthreads(),), low=-np.infty, high=np.infty, dtype=np.int32)
            observation_space = spaces.Tuple((env.observation_space, bthreads_obs_space))
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

    def step(self, action):
        observation, reward, terminated, truncated, info = self.env.step(action)
        set_state(observation)
        
        if (self.add_strategies):
            # advance the bprogram
            self.bprog.choose_event(BEvent(str(self._get_tuple_action(action))))
            obs_strats = np.array(self._get_strategies_progress())
            observation = (observation,obs_strats )
            # print(obs_strats)
    
        return observation, reward, terminated, truncated, info 
    
    def reset(self,seed=None, options=None):

        observation, info = self.env.reset()
        set_state(observation)

        if (self.add_strategies):
            self._reset_strategies()
            obs_strats = np.array(self._get_strategies_progress())
            observation = (observation, obs_strats )

        return observation, info
    
    def render(self):
        return self.env.render()
    
    def close(self):
        return self.env.close()

    def _get_strategies_progress(self):
        return list(bthreads_progress.values())
    
    def _reset_strategies(self):
        bprogram = BProgram(bthreads=create_strategies(), event_selection_strategy=SimpleEventSelectionStrategy())
        self.bprog.reset(bprogram)
        reset_all_progress()