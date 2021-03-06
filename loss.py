import torch
from torch import nn as nn
from torchvision.models.vgg import vgg19
import torchvision.transforms as transforms
import torch.autograd as autograd


class Normalization(nn.Module):
    def __init__(self, mean, std, device="cpu"):
        super(Normalization, self).__init__()
        self.mean = torch.tensor(mean).to(device).view(-1, 1, 1)
        self.std = torch.tensor(std).to(device).view(-1, 1, 1)

    def forward(self, img):
        return (img - self.mean) / self.std


class PerceptualNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = vgg19(pretrained=True)
        features_slice = vgg.features[:35]
        perceptual_network = nn.Sequential(*features_slice).eval()
        for param in perceptual_network.parameters():
            param.requires_grad = False
        self.perceptual_network = perceptual_network

    def forward(self, inputs):
        return self.perceptual_network(inputs)


class PerceptualLoss(nn.Module):
    def __init__(self, device="cpu"):
        super().__init__()
        self.normalization = Normalization(
            [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], device
        )
        self.perceptual_network = PerceptualNetwork().to(device)
        self.mse_loss = nn.MSELoss()

    def forward(self, input_a, input_b):
        input_a = self.normalization(input_a)
        input_b = self.normalization(input_b)
        return self.mse_loss(
            self.perceptual_network(input_a), self.perceptual_network(input_b)
        )


def calc_grad_pen(dis_net, hr_sample, sr_sample, device):
    alpha = (
        torch.rand(sr_sample.size()[0], 1, 1, 1).expand(*sr_sample.size()).to(device)
    )
    interpolates = autograd.Variable(
        alpha * sr_sample.detach() + (1 - alpha) * hr_sample.detach()
    )
    interpolates.requires_grad_(True)
    int_dis = dis_net(interpolates)

    gradients = autograd.grad(
        outputs=int_dis,
        inputs=interpolates,
        grad_outputs=torch.ones(int_dis.size()).to(device),
        create_graph=True,
        retain_graph=True,
        only_inputs=True,
    )[0]

    gradients = gradients.view(gradients.size(0), -1)

    return ((gradients.norm(2, dim=1) - 1) ** 2).mean()
