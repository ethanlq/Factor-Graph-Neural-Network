import torch
from .mp_nn import mp_conv_v2, mp_conv_type
from .mp_nn_double import mp_conv_double
from .base_model import base_mp_nn
SyncBatchNorm = torch.nn.BatchNorm2d


class mp_conv_residual(base_mp_nn):
    def __init__(self,
                 nin,
                 nmed,
                 netype,
                 extension=mp_conv_type.ORIG_WITH_DIFF,
                 with_residual=True,
                 with_hop=False):
        """
        Residual block for graph conv network.
        :param nin: number of input units
        :param nmed: number of units in the graph conv layer 
        :param netype: number of edge types 
        :param extension: organization type of edge features
        :param with_residual: use residual link or not
        """
        super(mp_conv_residual, self).__init__()
        self.conv1 = torch.nn.Sequential(torch.nn.Conv2d(nin, nmed, 1),
                                         SyncBatchNorm(nmed),
                                         torch.nn.ReLU(inplace=True))
        self.mp_conv = mp_conv_double(nmed, nmed, nmed, netype, extension=extension) \
            if with_hop else mp_conv_v2(nmed, nmed, netype, extension=extension)

        self.conv2 = torch.nn.Sequential(torch.nn.Conv2d(nmed, nin, 1),
                                         SyncBatchNorm(nin),
                                         torch.nn.ReLU(inplace=True))
        self.with_residual = with_residual
        self.with_hop = with_hop

    def forward(self, node_feature, nn_idx, etype):
        """
        Forward function.
        :param node_feature: node feature
        :param nn_idx: graph link list 
        :param etype: edge types
        """
        # print(node_feature.shape)
        # v1,v2,v3,v4 = argv
        # print(v1.shape, v2.shape, v3.shape, v4.shape)
        nfeature = self.conv1(node_feature)
        nfeature = self.mp_conv(nfeature, nn_idx, etype)
        nfeature = self.conv2(nfeature)

        if self.with_residual:
            nfeature = nfeature + node_feature

        return nfeature
