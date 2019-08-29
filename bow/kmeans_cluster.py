import time
import numpy as np
import torch
from pykeops.torch import LazyTensor
import argparse
import os


use_cuda = torch.cuda.is_available()
dtype = 'float32' if use_cuda else 'float64'
torchtype = {'float32': torch.float32, 'float64': torch.float64}
cuda0 = torch.device('cuda:0')


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for K-mean clustering")
    parser.add_argument('features_file_path')
    parser.add_argument('output_folder')
    parser.add_argument('--checkpoint_filepath', dest='checkpoint_filepath')
#    parser.add_argument('max_iter', type=int)
    return parser.parse_args()

args = create_argparse()


#def MiniBatchKMeans(x, K, Niter=300, verbose=True):
#    print("Start MiniBatchKMeans clustering")
#    N, D = x.shape
#    start = time.time()



def KMeans(x, K, checkpoint_filepath=None, Niter=20, verbose=True):
    print("Start K-Means clustering")
    N, D = x.shape
    start = 0
    if checkpoint_filepath is not None:
        c = torch.load(checkpoint_filepath)
        start = int(os.path.basename(checkpoint_filepath).split('.')[0])
        print("Load checkpoint {}...".format(checkpoint_filepath))
    else:
        c = x[:K, :].clone()
        print("Initialize new center...")
    batch_size = N // 1000 + 1
    Nbatch_iter = N // batch_size
    print("Number of batch iterations: {}".format(Nbatch_iter))
    print("Number of clusters: {}".format(K))
    print("Number of data: {}".format(N))
    for i in range(start, Niter):
        print("--- Iteration {}...".format(i+1))
        start = time.time()
        new_center = torch.zeros(c.shape, dtype=torchtype[dtype])
        c_i = LazyTensor(c[None, :, :])
        #c_i = c[None, :, :]
        Ncl_i = torch.zeros(K, dtype=torchtype[dtype])
        total_inertial = 0.0
        for j in range(Nbatch_iter):
            b_start = time.time()
            fr = j * batch_size
            to = min((j+1) * batch_size, N)
            x_j = LazyTensor(x[fr:to, None, :])
            #x_j = x[fr:to, None, :]
            D_ij = ((x_j - c_i) ** 2).sum(-1)
            inertial = ((D_ij.min(dim=1))**(0.5)).sum()
            total_inertial += inertial
            cl = D_ij.argmin(dim=1).long().view(-1)
            Ncl_ij = torch.bincount(cl, minlength=K).type(torchtype[dtype])
            Ncl_i += Ncl_ij
            for d in range(D):
                weights = torch.bincount(cl, weights=x[fr:to, d], minlength=K)
                new_center[:, d] += weights
            b_end = time.time()
            print("*** Running batch {} from {} to {} takes {}s".format(j+1, fr, to, b_end-b_start))
        c = new_center / Ncl_i[:, None]
        end = time.time()
        print('--> Iteration {} - Inertial: {} - Time: {}s'.format(i+1, total_inertial, end-start))
        torch.save(c, os.path.join(args.output_folder, '{:02d}.ckpt'.format(i+1)))
    return c


if __name__ == '__main__':
    #N, D, K = 20000000, 128, 2000000
    #N, D, K = 100, 2, 3
    #x = torch.randn(N, D, dtype=torchtype[dtype], device=cuda0) 
    #args = create_argparse()
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    x = np.load(args.features_file_path)
#    K = x.shape[0] // 1000
    K = 32768
    x = torch.Tensor(x).type(torchtype[dtype])
    c = KMeans(x, K, checkpoint_filepath=args.checkpoint_filepath)

