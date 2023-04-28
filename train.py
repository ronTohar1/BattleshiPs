# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3.dqn import DQN
import gym_battleship
import gymnasium
import gym
from bp_gym import BPGymEnv
from gymnasium.wrappers.flatten_observation import FlattenObservation
from gymnasium.wrappers.compatibility import EnvCompatibility

def train():
    # run = 
    env = gymnasium.make('Battleship-v0')
    env = BPGymEnv(env)
    env = FlattenObservation(env)

    # model = DQN('MlpPolicy', env, verbose=1, tensorboard_log="./tensorboard/")
    # model.learn(total_timesteps=10000, callback=NeptuneCallback())
    # model.learn(total_timesteps=10_000,tb_log_name="first_run")

def game_loop():
    # env = gymnasium.make('Battleship-v0')
    env = gymnasium.make("Battleship-v0")
    env = BPGymEnv(env)
    env = FlattenObservation(env)
    obs = env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        # print("yea")
        # print(obs)
        # env.render()
        


if __name__ == '__main__':
    # train()
    game_loop()