from pathlib import Path
import argparse
import os
import numpy as np
from collections import Counter, defaultdict
from pykeops.torch import LazyTensor
import math
import argparse
import torch
import sys
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent))
from utils.exec_multiprocess import MultiProcessTask


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for feature quantization")
    parser.add_argument('feature_folder_path')
    parser.add_argument('cluster_center_file_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


args = create_argparse()
cluster_centers = torch.load(args.cluster_center_file_path)
num_clusters, dimension = cluster_centers.shape


def create_params(args):
    print('Creating quantization params...')
    params = []
    output_folder_path = os.path.join(args.output_folder_path, 'term_freq')
    for root, _, files in os.walk(args.feature_folder_path):
        for f in files:
            file_name = os.path.basename(f).split('.')[0]
            feature_file_path = os.path.join(root, f)
            output_file_path = feature_file_path.replace(args.feature_folder_path, output_folder_path)
            params.append([feature_file_path, output_file_path])
    return params


def generate_term_freq(params):
    feature_file_path, output_file_path = params
    output_folder = os.path.dirname(output_file_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if os.path.exists(output_file_path):
        return
    print("Quantization {}...".format(feature_file_path))
    feat = np.load(feature_file_path)
    N, _ = feat.shape
    feat = torch.Tensor(feat).type(torch.float32)
    c = torch.Tensor(cluster_centers[None, :, :]).type(torch.float32)
    # Transform feature matrix to perform fast matrix multiplication
    feat = LazyTensor(feat[:, None, :])
    c = LazyTensor(c)
    dist = ((feat - c) ** 2).sum(-1)
    preds = dist.argmin(dim=1).long().view(-1)
    term_freq = torch.bincount(preds, minlength=num_clusters).type(torch.float32).numpy()
    normed_term_freq = term_freq / np.linalg.norm(term_freq)
    np.save(output_file_path, normed_term_freq)


def combine_term_freq_into_one_file(term_freq_folder):
    combined_feats = []
    for root, _, files in os.walk(term_freq_folder):
        for f in files:
            file_path = os.path.join(root, f)
            feat = np.load(file_path)
            combined_feats.append(feat)
    combined_feats = np.vstack(np.array(combined_feats)) 
    return combined_feats


def generate_idf(total_images, tf_total):
    idf = np.zeros((num_clusters, 1))
    for i in range(num_clusters):
        n_qi = np.where(tf_total[:, i] > 0)[0].shape[0]
        idf[i] = math.log(total_images / n_qi) if n_qi > 0 else 0
    idf = idf.reshape(num_clusters)
    return idf


if __name__ == '__main__':
    params = create_params(args)
    total_images = params.__len__()
    for p in params:
        generate_term_freq(p)
    #mtp = MultiProcessTask(params, generate_term_freq)
    #mtp.run_multiprocess()
    # Combine term frequency vector
    print('Combining term frequency into one file...')
    term_freq_folder = os.path.join(args.output_folder_path, 'term_freq')
    combined_term_freq_output = os.path.join(args.output_folder_path, 'combined_term_freq.npy')
    if not os.path.exists(combined_term_freq_output):
        combined_term_freq = combine_term_freq_into_one_file(term_freq_folder)
        try:
            np.save(combined_term_freq_output, combined_term_freq)
        except:
            print("Not enough memory!!!")
    else:
        combined_term_freq = np.load(combined_term_freq_output)

    # Create idf vector
    print('Creating inverse document frequency...')
    idf_filepath = os.path.join(args.output_folder_path, 'idf.npy')
    if os.path.exists(idf_filepath): 
        exit(0)
    idf = generate_idf(total_images, combined_term_freq)
    np.save(idf_filepath, idf)
