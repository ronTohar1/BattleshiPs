import gymnasium
from gymnasium import spaces
import util
from bppy import BProgram
from bp_wrapper import BPwrapper
from strategy_bthreads import create_strategies, number_of_bthreads, bthreads_progress, reset_all_progress
from priority_event_selection_strategy import PriorityEventSelectionStrategy
import numpy as np
from gymnasium.wrappers.compatibility import EnvCompatibility
# from gymnasium.wrappers.step_api_compatibility import StepAPICompatibility
from gymnasium.utils.env_checker import check_env

class BPGymEnv(gymnasium.Env):
    def __init__(self, env):

        self.env = env
        try:
            if not check_env(env):
                self.env = EnvCompatibility(env)
        except:
            self.env = EnvCompatibility(env)

        self.action_space = env.action_space
        self.observation_space = env.observation_space

        # initialize the bprogram containing the strategies
        if (util.ADD_STRATEGIES):
            # bthreads observation space is a box with number of bthreads with each value between -inf and inf, and should be integer
            bthreads_obs_space = spaces.Box(shape=(number_of_bthreads(),), low=-np.infty, high=np.infty, dtype=np.int32)
            observation_space = spaces.Tuple((env.observation_space, bthreads_obs_space))
            self.observation_space = observation_space

            self.bprog = BPwrapper()
            bprogram = BProgram(bthreads=create_strategies(), event_selection_strategy=PriorityEventSelectionStrategy())
            self.bprog.reset(bprogram)


    def step(self, action):
        observation, reward, terminated, truncated, info = self.env.step(action)

        if (util.ADD_STRATEGIES):
            # advance the bprogram
            self.bprog.advance_randomly()
            obs_strats = self._get_strategies_progress() + [1]
            observation = (observation,obs_strats )
        
        return observation, reward, terminated, truncated, info 
    
    def reset(self,seed=None, options=None):

        observation, info = self.env.reset()
        if (util.ADD_STRATEGIES):
            self._reset_strategies()
            obs_strats = self._get_strategies_progress() + [1]
            observation = (observation,obs_strats )

            
        return observation
    
    def render(self):
        return self.env.render()
    
    def close(self):
        return self.env.close()

    def _get_strategies_progress(self):
        return list(bthreads_progress.values())
    
    def _reset_strategies(self):
        bprogram = BProgram(bthreads=create_strategies(), event_selection_strategy=PriorityEventSelectionStrategy())
        self.bprog.reset(bprogram)
        reset_all_progress()