# Training many models in Slurm

import os
import sys
import subprocess
import argparse
from itertools import product


def main():
    # Assuming there is a script called train_bships.sh that takes the following arguments:
    # --episodes, --log_path, --verbose, --agent, --lr, --gamma
    # and that it is located in the same directory as this script

    parser = argparse.ArgumentParser()
    parser.add_argument('--bp_strats','-bp',type=bool, default=False, help='Use BP strategies for the agent')
    parser.add_argument('--verbose','-v',type=int, default=0, help='Verbose level for the agent')
    parser.add_argument('--log_path','-log',type=str, default='./tensorboard_log/', help='Path to tensorboard log directory')
    args = parser.parse_args()


    episodes = [10_000_000, 15_000_000]
    log_path = args.log_path
    verbose = args.verbose
    agents = ['dqn', 'a2c', 'ppo']
    lrs = [0.0001, 0.001, -1]
    gammas = [0.99]
    
    counter = 0
    for ep, lr, gamma, agent in product(episodes, lrs, gammas, agents):
        counter +=1
        r = subprocess.run(['sbatch', 'train_bships.sh', str(ep), log_path, str(verbose), agent, str(lr), str(gamma), str(args.bp_strats)])
        print(f"({counter})",f"Ran with args: ep-{ep}, log_path-{log_path}, verbose-{verbose}, agent-{agent}, lr-{lr}, gamma-{gamma}, bp-{args.bp_strats}, and got return code: ", r.returncode)

if __name__ == '__main__':
    main()