# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3 import A2C, DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
import gym_battleship
import gymnasium
# import gym
from bp_gym import BPGymEnv
from gymnasium.wrappers.flatten_observation import FlattenObservation
import numpy as np
from stable_baselines3.common.logger import configure

def train():
    # run = 
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = BPGymEnv(env)
    env = FlattenObservation(env) # Flattening observations to be able to use observation space for agent
    # env = Monitor(env, filename="bla.txt", allow_early_resets=True) # Wrapper from sb3 to monitor more gym info
    log_path ="./tensorboard_log/"
    agent = DQN('MlpPolicy', env, tensorboard_log=log_path)
    # agent = A2C('MlpPolicy', env)
    # logger = configure(log_path, ["tensorboard", "stdout"])
    # agent.set_logger(logger)
    agent.learn(total_timesteps=10_000_000, tb_log_name="DQN1", reset_num_timesteps=False, log_interval=5, progress_bar=True)

    # q: how to log the dqn loss?
    # a: https://stable-baselines3.readthedocs.io/en/master/guide/examples.html#logging-progress

    # dqn.learn(total_timesteps=5000, tb_log_name="dqn11", reset_num_timesteps=False, log_interval=10)


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
    # game_loop()