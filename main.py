import torch

from networks.generator import Generator
from networks.discriminator import Discriminator
from loss import PerceptualLoss
import torch.nn as nn
import argparse
import os
import random
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
import numpy as np
from tqdm import tqdm, trange
HR_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
])
LR_TRANSFORM = transforms.Compose([
    transforms.Resize(128),
    transforms.ToTensor(),
])
class CustomImageFolder(dset.ImageFolder):
    def __init__(self, root, transform=HR_TRANSFORM, lr_transform=LR_TRANSFORM):
        super(CustomImageFolder, self).__init__(root, transform=transform)
        self.lr_transform = lr_transform
        self.imgs = self.samples
    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        path, _ = self.samples[index]
        sample = self.loader(path)


        if self.transform is not None:
            hr_sample = self.transform(sample)
        if self.lr_transform is not None:
            lr_sample = self.lr_transform(sample)
        return hr_sample, lr_sample


if __name__ == "__main__":
    # gen_net = Generator()
    # images = torch.randn(5, 3, 128, 128)
    # print(gen_net)
    # output = gen_net(images)
    # print(output.shape)
    #
    # dis_net = Discriminator()
    # print(dis_net)
    # print(dis_net(output).shape)
    # perceptual_loss = PerceptualLoss()
    dataroot = "dataset/"
    dataset = CustomImageFolder(root=dataroot)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1)
    batch = next(iter(dataloader))

    gen_net = Generator(num_res_blocks=2)
    perceptual_loss = PerceptualLoss()
    lr = 0.0002
    beta1 = 0.5

    optimizerG = optim.Adam(gen_net.parameters(), lr=lr, betas=(beta1, 0.999))


    for epoch in range(100):
        for hr_sample, lr_sample in dataloader:
            gen_net.zero_grad()
            sr_sample = gen_net(lr_sample)
            loss = perceptual_loss(hr_sample, sr_sample)
            loss.backward()
            optimizerG.step()
            print(loss)
            break