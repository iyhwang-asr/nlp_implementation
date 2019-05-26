import torch
import torch.nn as nn
from model.ops import Permute, Flatten, ConvBlock
from typing import Dict


class VDCNN(nn.Module):
    """VDCNN class"""
    def __init__(self, num_classes: int, embedding_dim: int, k_max: int, dic: Dict[str, int]) -> None:
        """Instantiating VDCNN class

        Args:
            num_classes (int): the number of classes
            embedding_dim (int): embedding dimension of token
            k_max (int): parameter of k-max pooling following last convolution block
            dic (dict): token2idx
        """
        super(VDCNN, self).__init__()
        self._extractor = nn.Sequential(nn.Embedding(len(dic), embedding_dim, 0),
                                        Permute(),
                                        nn.Conv1d(embedding_dim, 64, 3, 1, 1),
                                        ConvBlock(64, 64),
                                        ConvBlock(64, 64),
                                        nn.MaxPool1d(2, 2),
                                        ConvBlock(64, 128),
                                        ConvBlock(128, 128),
                                        nn.MaxPool1d(2, 2),
                                        ConvBlock(128, 256),
                                        ConvBlock(256, 256),
                                        nn.MaxPool1d(2, 2),
                                        ConvBlock(256, 512),
                                        ConvBlock(512, 512),
                                        nn.AdaptiveMaxPool1d(k_max),
                                        Flatten())

        self._classifier = nn.Sequential(nn.Linear(512 * k_max, 2048),
                                         nn.ReLU(),
                                         nn.Linear(2048, 2048),
                                         nn.ReLU(),
                                         nn.Linear(2048, num_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feature = self._extractor(x)
        score = self._classifier(feature)
        return score