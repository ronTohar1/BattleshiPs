# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3.dqn import DQN
import gym_battleship
import gymnasium as gym
from bp_gym import BPGymEnv
from gymnasium.wrappers.flatten_observation import FlattenObservation
def train():
    # run = 
    env = gym.make('Battleship-v0')
    env = BPGymEnv(env)
    env = FlattenObservation(env)
    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log="./tensorboard/")
    # model.learn(total_timesteps=10000, callback=NeptuneCallback())
    model.learn(total_timesteps=10_000,tb_log_name="first_run")


if __name__ == '__main__':
    train()