# import neptune
# from neptune.integrations.tensorflow_keras import NeptuneCallback
from stable_baselines3 import A2C, DQN,PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
import gym_battleship
import gymnasium
# import gym
from bp_gym import BPGymEnv
from wrap_battleships import BattleshipsWrapper
from gymnasium.wrappers.flatten_observation import FlattenObservation
import numpy as np
from stable_baselines3.common.logger import configure
import argparse
import util
import torch as th
from custom_cnn import BattleshipsCNN
from resnet import ResNetCNN

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
    parser.add_argument('--agent','-a',type=str, default='a2c', choices=['a2c','dqn','ppo'], help='Agent to use for training')
    parser.add_argument('--lr','-lr',type=float, default=0.0001, help='Learning rate for the agent')
    parser.add_argument('--gamma','-g',type=float, default=0.99, help='Discount factor for the agent')
    parser.add_argument('--bp_strats','-bp',action="store_true", help='Use BP strategies for the agent')
    parser.add_argument('--no_bp_strats','-nobp',action="store_true", help='Dont use BP strategies for the agent')
    parser.add_argument('--net_arch','-na',type=str, default='[64,64]', help='Network architecture for the agent')
    parser.add_argument('--activation_fn','-af',type=str, default='tanh', choices=['tanh','relu'], help='Activation function for the agent')
    parser.add_argument('--policy','-p',type=str, default='CnnPolicy', choices=['MlpPolicy', 'CnnPolicy'], help='Policy to use for the agent')
    parser.add_argument('--features_dim','-fd',type=int, default=512, help='Number of features for the last layer of the CNN')
    parser.add_argument('--model_type','-mt',type=str, default='cnn', choices=['resnet','cnn'], help='Type of model to use for the agent')
    args = parser.parse_args()


    
    num_ep = args.episodes / 1_000_000
    using_strategies = args.bp_strats
    net_arch = eval(args.net_arch)
    activation_fn_name = args.activation_fn.lower()
    activation_fn = th.nn.Tanh if activation_fn_name == 'tanh' else th.nn.ReLU
    # default net for ppo/dqn/a2c is 2 hidden layers with 64 neurons each
    policy_kwargs = dict(activation_fn=activation_fn, 
                     net_arch=net_arch)
    learning_rate = args.lr if (args.lr and args.lr != -1) else lambda prog: 0.00001 * (1 - prog) + 0.01 * prog
    gamma = args.gamma
    log_path = args.log_path
    verbose = args.verbose
    agent_name = args.agent.lower()
    policy = args.policy
    features_dim = args.features_dim
    model_type = args.model_type.lower()
    model = BattleshipsCNN if model_type == 'cnn' else ResNetCNN

    if policy == 'CnnPolicy':
        policy_kwargs["features_extractor_class"] = model
        policy_kwargs["features_extractor_kwargs"] = {"normalized_image":True,
                                                      "features_dim": features_dim,
                                                      "activation_fn": activation_fn} # All normalized (0 or 1 anyways)

    
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0", make_kwargs={'board_size':(util.BOARD_SIZE, util.BOARD_SIZE)})
    env = BattleshipsWrapper(env) # Wrapping the env to be 1 channel instead of 2 channels of the board
    env = BPGymEnv(env, add_strategies=using_strategies)
    # env = FlattenObservation(env) # Flattening observations to be able to use observation space for agent

    
    agent_args = {  'policy': policy,
                    'env':env,
                    'learning_rate':learning_rate,
                    'gamma':gamma,
                    'tensorboard_log':log_path, 
                    'verbose':verbose, 
                    # 'policy_kwargs':policy_kwargs
                }
    agent = None
    if agent_name == 'dqn':
        agent = DQN(policy_kwargs=policy_kwargs, **agent_args)
    elif agent_name == 'a2c':
        agent = A2C(policy_kwargs=policy_kwargs ,**agent_args)
    elif agent_name == 'ppo':
        agent = PPO(policy_kwargs=policy_kwargs, **agent_args)

    # print("Using strategies: ", using_strategies)
    # print(agent)
    # run_name = f"{agent_name}_{num_ep}M_alpha-{learning_rate if (learning_rate!=-1) else 'function'}_gamma-{gamma}_arch-{net_arch}_af-{activation_fn_name}_pol-{policy}_feature_dim-{features_dim}"+("_bp" if using_strategies else "")
    run_name = f"{agent_name}_{num_ep}M_alpha-{learning_rate if (learning_rate!=-1) else 'function'}_gamma-{gamma}_arch-{net_arch}_pol-{policy}"
    if policy == 'CnnPolicy':
        run_name += f"_feature_dim-{features_dim}_model-{model_type}"
    elif policy == 'MlpPolicy':
        run_name += f"_af-{activation_fn_name}"
    run_name = run_name+("_BP" if using_strategies else "_NOPB")
    # agent.learn(total_timesteps=args.episodes, tb_log_name=run_name, reset_num_timesteps=True, log_interval=100, progress_bar=False)
    x = agent.policy.__str__()
    print(x)
    # print(PPO("CnnPolicy", gymnasium.make("CarRacing-v2")).policy)
    # policy_kwargs={"features_extractor_kwargs": {"normalized_image":False}}
        
if __name__ == '__main__':
    main()
    # game_loop()