# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3 import A2C, DQN,PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
import gym_battleship
import gymnasium
# import gym
from bp_gym import BPGymEnv
from gymnasium.wrappers.flatten_observation import FlattenObservation
import numpy as np
from stable_baselines3.common.logger import configure
import argparse

def train():
    # run = 
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = BPGymEnv(env)
    env = FlattenObservation(env) # Flattening observations to be able to use observation space for agent
    # env = Monitor(env, filename="bla.txt", allow_early_resets=True) # Wrapper from sb3 to monitor more gym info
    log_path ="./tensorboard_log/"
    agent = DQN('MlpPolicy', env, tensorboard_log=log_path,verbose=1,)
    # agent = A2C('MlpPolicy', env)
    # logger = configure(log_path, ["tensorboard", "stdout"])
    # agent.set_logger(logger)
    agent.learn(total_timesteps=1_000_000, tb_log_name="DQN2", reset_num_timesteps=True, log_interval=5, progress_bar=False)

    # q: how to log the dqn loss?
    # a: https://stable-baselines3.readthedocs.io/en/master/guide/examples.html#logging-progress

    # dqn.learn(total_timesteps=5000, tb_log_name="dqn11", reset_num_timesteps=False, log_interval=10)


def game_loop():
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    # env = BPGymEnv(env)
    check_env(env)
    # env = FlattenObservation(env)
    # obs,_ = env.reset()
    # done = False
    # while not done:
    #     action = env.action_space.sample()
    #     obs, reward, terminated, truncated, info = env.step(action)
    #     done = terminated or truncated
    #     env.render()        

def main():
    parser = argparse.ArgumentParser()
    # parser takes 'episodes', 'log_name', 'agent' (dqn, a2c, ppo), 'lr' (learning rate), 'gamma' (discount factor)
    parser.add_argument('--episodes','-e',type=int, default=3_000_000, help='Number of episodes to train the agent')
    parser.add_argument('--log_path','-l',type=str, default='./tensorboard_log/', help='Name of the log file')
    parser.add_argument('--verbose','-v',type=int, default=0, help='Verbosity of the agent')
    parser.add_argument('--agent','-a',type=str, default='dqn', help='Agent to use for training')
    parser.add_argument('--lr','-lr',type=float, default=None, help='Learning rate for the agent')
    parser.add_argument('--gamma','-g',type=float, default=0.99, help='Discount factor for the agent')
    args = parser.parse_args()

    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = BPGymEnv(env)
    env = FlattenObservation(env) # Flattening observations to be able to use observation space for agent

    learning_rate = args.lr if (args.lr and args.lr != -1) else lambda prog: 0.1 * (1 - prog) + 0.0001 * prog
    # agent_args = ('MlpPolicy', env, learning_rate=learning_rate, gamma=args.gamma, tensorboard_log=args.log_path, verbose=args.verbose)
    agent_args = {'policy':'MlpPolicy', 'env':env, 'learning_rate':learning_rate, 'gamma':args.gamma, 'tensorboard_log':args.log_path, 'verbose':args.verbose}
    agent = DQN(**agent_args)
    if args.agent.lower() == 'a2c':
        agent = A2C(**agent_args)
    elif args.agent.lower() == 'ppo':
        agent = PPO(**agent_args)

    num_ep = args.episodes / 1_000_000
    run_name = f"{args.agent}_{num_ep}M_α-{args.lr if args.lr else 'λ'}_Γ-{args.gamma}"
    agent.learn(total_timesteps=args.episodes, tb_log_name=run_name, reset_num_timesteps=True, log_interval=5, progress_bar=False)
        
if __name__ == '__main__':
    main()
    # game_loop()