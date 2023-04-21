import numpy as np
import gym_battleship
import gym
from collections import namedtuple
from bp_gym import BPGymEnv


def main():
    env = gym.make('AdverserialBattleship-v0')
    step = namedtuple('step', ['state', 'reward', 'done', 'info'])

    

def example_run():
    env = gym.make('Battleship-v0')
    env = BPGymEnv(env)
    print(env.observation_space)
    print(env.action_space)
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
    # main()
    example_run()