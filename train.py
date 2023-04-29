# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3.dqn import DQN
from stable_baselines3.common.env_checker import check_env
import gym_battleship
import gymnasium
# import gym
from bp_gym import BPGymEnv
from gymnasium.wrappers.flatten_observation import FlattenObservation
import numpy as np

def train():
    # run = 
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    # print("spec:",env.spec)
    env = BPGymEnv(env)
    # print("obs space:",env.observation_space.shape)
    # print("obs space:",env.observation_space)
    # print("spec:",env.spec)
    env = FlattenObservation(env)
    # print("spec:",env.spec)
    # print("obs space 222: ", env.observation_space.shape)
    # print("obs space 222: ", env.observation_space)
    dqn = DQN('MlpPolicy', env, verbose=2, tensorboard_log="./tensorboard_log/")
    dqn.learn(total_timesteps=10000)


def game_loop():
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = BPGymEnv(env)
    # env = FlattenObservation(env)
    obs,_ = env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        env.render()        


if __name__ == '__main__':
    train()
    # try_some()
    # game_loop()