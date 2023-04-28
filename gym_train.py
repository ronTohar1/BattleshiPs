# import gym 
import gym_battleship
import gymnasium
from gymnasium.wrappers import FlattenObservation


def train():
    # env = gym.make()
    env = gymnasium.make("GymV21Environment-v0", env_id="Battleship-v0")
    env = FlattenObservation(env)
    print(f'{env=}, {env.action_space=}, {env.observation_space=}')
    obs = env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        env.render()


if __name__ == '__main__':
    train()