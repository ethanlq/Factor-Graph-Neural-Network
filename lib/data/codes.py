import torch
from torch.utils.data import Dataset

import numpy as np
import pathlib
import os
import tempfile
import subprocess
from .MNC import init_seed, s2t, t2y


def get_snr(snr_db):
    return 10**(snr_db/10)


class LDPCGenerator:
    def __init__(self):
        self.code_len = 48
        self.Gfile = os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            './MNC/codes/96.3.963/G'
        )
        self.ldpc_file = os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            '../../ldpc_data/96.3.963'
        )
        self.get_factor_sturcture()

    def get_factor_sturcture(self):
        with open(self.ldpc_file) as f:
            for i in range(4):
                f.readline()

            for i in range(96):
                indice = map(lambda x: int(x)-1, f.readline().strip().split())

            factors = []

            for i in range(48):
                indice = map(lambda x: int(x)-1, f.readline().strip().split())
                cfactor = []
                for j, idx in enumerate(indice):
                    cfactor.append(idx)

                factors.append(cfactor)

            self.factors = np.asarray(factors, np.int)

    def __call__(self, snr_db, sigma_b):

        s = np.random.randint(0, 2, self.code_len)
        t = s2t(s, 48, 48, self.Gfile, True)
        y = t2y(t, snr_db, sigma_b, 0.05)
        return s, t, y

    def get_highorder_feature(self, y):

        return np.take(y, self.factors.reshape(-1)).reshape(self.factors.shape)


class Codes(Dataset):
    def __init__(self, filename, train=True):
        self.data = torch.load(filename)
        self.node_feature = self.data['node_feature']
        self.hop_feature = self.data['hop_feature']
        self.y = self.data['y']

        if not train:
            self.sigma_b = self.data['sigma_b']
        else:
            self.sigma_b = torch.zeros((len(self.node_feature)))

        self.len = len(self.node_feature)
        self.generator = LDPCGenerator()

    def __len__(self):
        return self.len

    def __getitem__(self, idx):

        node_feature = self.node_feature[idx].numpy().squeeze().T[:, 0]
        hop = self.generator.get_highorder_feature(node_feature)
        hop_feature = np.expand_dims(hop.T, -1)

        node_feature = self.node_feature[idx].squeeze()
        # print(node_feature[1, :])
        node_feature[1, :] = 10 * torch.log10(node_feature[1, :])
        # print(node_feature)
        return node_feature.unsqueeze(-1), hop_feature, self.y[idx], self.sigma_b[idx]


class ContinusCodes(Dataset):
    def __init__(self):
        self.len = 10000
        self.sigma_b = [0, 1, 2, 3, 4, 5]
        self.snr_db = [0, 1, 2, 3, 4]
        self.generator = LDPCGenerator()

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        sigma_b = np.random.choice(self.sigma_b)
        snr_db = np.random.choice(self.snr_db)

        orig, trans, trans_noizy = self.generator(snr_db, sigma_b)
        hop = self.generator.get_highorder_feature(trans_noizy)

        node_feature = np.asarray([[elem, snr_db]
                                   for elem in trans_noizy], dtype=np.float32).T
        hop_feature = np.expand_dims(hop.T, -1)

        return node_feature.astype(np.float32), hop_feature.astype(np.float32), trans.astype(np.int), sigma_b
