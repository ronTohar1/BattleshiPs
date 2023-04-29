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
    
    episodes = [3_000_000, 5_000_000, 10_000_000, 15_000_000]
    log_path = './tensorboard_log/'
    verbose = 0
    agents = ['dqn', 'a2c', 'ppo']
    lrs = [0.0001, 0.001, -1]
    gammas = [0.99]
    
    counter = 0
    for ep, lr, gamma, agent in product(episodes, lrs, gammas, agents):
        counter +=1
        r = subprocess.run(['sbatch', 'train_bships.sh', str(ep), log_path, str(verbose), agent, str(lr), str(gamma)])
        print(f"({counter}) Ran with args: ", ep, log_path, verbose, agent, lr, gamma, " and got return code: ", r.returncode)

if __name__ == '__main__':
    main()