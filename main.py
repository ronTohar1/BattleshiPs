import numpy as np
import gym_battleship
# import gymnasium as gym
import gymnasium
from collections import namedtuple
from bp_gym import BPGymEnv
import util
# from gymnasium.spaces.utils import flatdim
from gymnasium.wrappers.compatibility import EnvCompatibility
import gymnasium
from gymnasium.wrappers import FlattenObservation

def main():
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0", make_kwargs={'board_size':(util.BOARD_SIZE, util.BOARD_SIZE)})
    print(f'{env=}, {env.action_space=}, {env.observation_space=}')
    print("Shpae is :",env.observation_space.shape[1:])

    
    

if __name__ == '__main__':
    main()