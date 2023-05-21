import gymnasium
import numpy as np

class BattleshipsWrapper(gymnasium.Env):

    def __init__(self, env):
        self.env = env
        self.action_space = env.action_space
        self.observation_space = gymnasium.spaces.Box(low=0, high=1, shape=env.observation_space.shape, dtype=np.float32)
        # self.observation_space = gymnasium.spaces.Box(low=0, high=255, shape=(1,10,10), dtype=np.uint8)

    # Return observation as one board
    def _modify_observation(self, observation):
        # 1 if hit, 2 if miss, 0 if unknown
        # new_obs = [[1 if observation[0][i][j] == 1 else 2 if observation[1][i][j] == 1 else 0 for j in range(10)] for i in range(10)]
        # return np.array(new_obs)
        return observation.astype(np.float32)
    

    def step(self, action):
        observation, reward, terminated, truncated, info = self.env.step(action)
        return self._modify_observation(observation), reward, terminated, truncated, info
    
    def reset(self):
        observation, info = self.env.reset()
        return self._modify_observation(observation), info
    
    def render(self):
        return self.env.render()
    
    def close(self):
        return self.env.close()