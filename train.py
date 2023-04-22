import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3.dqn import DQN
import gym_battleship
import gym
from bp_gym import BPGymEnv

def train():
    # run = 
    env = gym.make('Battleship-v0')
    env = BPGymEnv(env)
    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log="./tensorboard/")
    # model.learn(total_timesteps=10000, callback=NeptuneCallback())
    model.learn(total_timesteps=10_000,tb_log_name="first_run")


if __name__ == '__main__':
    train()