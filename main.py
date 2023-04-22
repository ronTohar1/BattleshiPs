import numpy as np
import gym_battleship
# import gymnasium as gym
import gymnasium as gym
from collections import namedtuple
from bp_gym import BPGymEnv

# from gymnasium.spaces.utils import flatdim
from gymnasium.wrappers.compatibility import EnvCompatibility

def main():
    # create pong environment
    env = gym.make("CartPole-v1",render_mode="human")
    # env = EnvCompatibility(env)

    # play an episode of random moves
    observation, info = env.reset()
    done = False
    while not done:
        env.render()
        action = env.action_space.sample()
        observation, reward, done,truncated, info = env.step(action)
    env.render()
    

def example_run():
    print("Asdfasfd")
    env = gym.make('Battleship-v0')
    env = BPGymEnv(env)
    print(env.observation_space)
    # print(flatdim(env.observation_space))
    # print(env.action_space)
    observation, reward, done, info = env.reset(),0, False, {}
    done = True
    # env.render()
    # print(env.board_generated)
    # while not done:
    #     action = env.action_space.sample()p
    #     observation, reward, done, info = env.step(action)
    #     env.render()
    #     # print(observation, reward, done, info)



if __name__ == '__main__':
    main()
    # example_run()