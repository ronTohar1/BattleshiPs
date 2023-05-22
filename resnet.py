from typing import Type
import torch
import torch.nn as nn
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch as th

class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.downsample = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        residual = self.downsample(residual)
        out += residual
        out = self.relu(out)

        return out


class ResNet(nn.Module):
    def __init__(self, ResBlock, layers, in_size, in_channels, out_features):
        super(ResNet, self).__init__()

        self.in_channels = 64
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self.make_layer(ResBlock, layers[0], out_channels=64, stride=1)
        self.layer2 = self.make_layer(ResBlock, layers[1], out_channels=128, stride=2)
        self.layer3 = self.make_layer(ResBlock, layers[2], out_channels=256, stride=2)
        self.layer4 = self.make_layer(ResBlock, layers[3], out_channels=512, stride=2)

        # num_ftrs = self._get_num_ftrs(in_size, in_channels)
        # self.regressor = nn.Sequential(
        #     nn.Linear(num_ftrs, num_linear_features),
        #     nn.ReLU(inplace=True),
        #     nn.Linear(num_linear_features, out_features)
        # )
        
    def _get_num_ftrs(self, in_size, in_channels):
        x = torch.randn(1, in_channels, in_size, in_size)
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
    
        return out.view(-1).shape[0]
        
    def make_layer(self, block, num_blocks, out_channels, stride):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)

        out = out.view(out.size(0), -1)
        # out = self.regressor(out)
        return out

def ResNet18(in_size, in_channels, out_features):
    return ResNet(ResBlock, [2, 2, 2, 2], in_size, in_channels, out_features)


class ResNetCNN(BaseFeaturesExtractor):
    def __init__(
        self,
        observation_space: gym.Space,
        features_dim: int = 512,
        normalized_image: bool = False,
        activation_fn: Type[nn.Module] = nn.ReLU,
    ) -> None:
        assert isinstance(observation_space, spaces.Box), (
            "NatureCNN must be used with a gym.spaces.Box ",
            f"observation space, not {observation_space}",
        )
        super().__init__(observation_space, features_dim)
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper
        n_input_channels = observation_space.shape[0]

        # Want to use 'same convolution' type of padding (padding='same'), and need for that stride=1
        # https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html
        self.cnn = ResNet18(observation_space.shape[1], n_input_channels, features_dim)
        # add flatten layer to cnn
        self.cnn = nn.Sequential(self.cnn, nn.Flatten())

        # Compute shape by doing one forward pass
        with th.no_grad():
            n_flatten = self.cnn(th.as_tensor(observation_space.sample()[None]).float()).shape[1]

        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())
        
    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.cnn(observations))