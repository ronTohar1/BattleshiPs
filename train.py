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
import util
import torch as th

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
    print("starting game loop")
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = BPGymEnv(env)
    env = FlattenObservation(env)
    print("Constructed env")
    obs,_ = env.reset()
    print("reset done")
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        # env.render()        

def main():
    parser = argparse.ArgumentParser()
    # parser takes 'episodes', 'log_name', 'agent' (dqn, a2c, ppo), 'lr' (learning rate), 'gamma' (discount factor)
    parser.add_argument('--episodes','-e',type=int, default=3_000_000, help='Number of episodes to train the agent')
    parser.add_argument('--log_path','-l',type=str, default='./tensorboard_log/', help='Name of the log file')
    parser.add_argument('--verbose','-v',type=int, default=0, help='Verbosity of the agent')
    parser.add_argument('--agent','-a',type=str, default='a2c', help='Agent to use for training')
    parser.add_argument('--lr','-lr',type=float, default=None, help='Learning rate for the agent')
    parser.add_argument('--gamma','-g',type=float, default=0.99, help='Discount factor for the agent')
    parser.add_argument('--bp_strats','-bp',action="store_true", help='Use BP strategies for the agent')
    parser.add_argument('--no_bp_strats','-nobp',action="store_true", help='Dont use BP strategies for the agent')
    parser.add_argument('--net_arch','-na',type=str, default='[64,64]', help='Network architecture for the agent')
    parser.add_argument('--activation_fn','-af',type=str, default='tahn', help='Activation function for the agent')
    # parser.add_argument('--bp_strats','-bp',type=bool, default=False, help='Use BP strategies for the agent')
    args = parser.parse_args()

    num_ep = args.episodes / 1_000_000
    using_strategies = args.bp_strats
    net_arch = eval(args.net_arch)
    activation_fn = th.nn.Tanh if args.activation_fn.lower() == 'tanh' else th.nn.ReLU
    # default net for ppo/dqn/a2c is 2 hidden layers with 64 neurons each
    policy_kwargs = dict(activation_fn=activation_fn,
                     net_arch=net_arch)

    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0", make_kwargs={'board_size':(util.BOARD_SIZE, util.BOARD_SIZE)})
    env = BPGymEnv(env, add_strategies=using_strategies)
    env = FlattenObservation(env) # Flattening observations to be able to use observation space for agent

    
    learning_rate = args.lr if (args.lr and args.lr != -1) else lambda prog: 0.00001 * (1 - prog) + 0.01 * prog
    agent_args = {  'policy':'MlpPolicy',
                    'env':env,
                    'learning_rate':learning_rate,
                    'gamma':args.gamma,
                    'tensorboard_log':args.log_path, 
                    'verbose':args.verbose, 
                    # 'policy_kwargs':policy_kwargs
                }
    agent = None
    if args.agent.lower() == 'dqn':
        agent = DQN(policy_kwargs=policy_kwargs, **agent_args)
    elif args.agent.lower() == 'a2c':
        agent = A2C(policy_kwargs=policy_kwargs ,**agent_args)
    elif args.agent.lower() == 'ppo':
        agent = PPO(policy_kwargs=policy_kwargs, **agent_args)

    run_name = f"{args.agent}_{num_ep}M_alpha-{args.lr if (args.lr and args.lr!=-1) else 'function'}_gamma-{args.gamma}_arch-{net_arch}_af-{args.activation_fn}"+("_bp" if args.bp_strats else "")
    agent.learn(total_timesteps=args.episodes, tb_log_name=run_name, reset_num_timesteps=True, log_interval=100, progress_bar=False)
        
if __name__ == '__main__':
    main()
    # game_loop()