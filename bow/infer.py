from pathlib import Path
import numpy as np
import cv2
import os
import torch
from pykeops.torch import LazyTensor
import argparse as ap
from sklearn.neighbors import NearestNeighbors


def create_argparse():
    parser = ap.ArgumentParser(description='Arguments for visual similary image retrieval')
    parser.add_argument('cluster_center_file_path')
    parser.add_argument('idf_file_path')
    parser.add_argument('vbow_total_file_path')
    parser.add_argument('image_path_order_file_path')
    parser.add_argument('input_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def load_model(vbow_total_filepath):
    print('Loading knn model...')
    vbow_total = np.load(vbow_total_filepath)
    neigh = NearestNeighbors(n_neighbors=500)
    neigh.fit(vbow_total)
    return neigh


args = create_argparse()
cluster_centers = torch.load(args.cluster_center_file_path)
num_clusters, dimension = cluster_centers.shape
idf = np.load(args.idf_file_path)
print("Loading image path order mapping...")
image_order = [line.rstrip() for line in open(args.image_path_order_file_path, 'r').readlines()]
model = load_model(args.vbow_total_file_path)


def extract_features(image_path):
    # Extract rootSIFT features
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift_detector = cv2.xfeatures2d.SIFT_create()
    _, desc = sift_detector.detectAndCompute(gray_image, None)
    eps = 1e-7
    desc /= (desc.sum(axis=1, keepdims=True) + eps)
    desc = np.sqrt(desc)
    return desc


def quantization(raw_feat):
    # Feature quantization
    raw_feat = torch.Tensor(raw_feat).type(torch.float32)
    c = torch.Tensor(cluster_centers[None, :, :]).type(torch.float32) 
    raw_feat = LazyTensor(raw_feat[:, None, :])
    c = LazyTensor(c)
    dist = ((raw_feat - c) ** 2).sum(-1)
    preds = dist.argmin(dim=1).long().view(-1)
    term_freq = torch.bincount(preds, minlength=num_clusters).type(torch.float32).numpy()
    normed_term_freq = term_freq / np.linalg.norm(term_freq)
    return normed_term_freq
 

def vbow_vectorize(tf, idf):
    vbow_feat = tf * idf
    normed_vbow_feat = vbow_feat / np.linalg.norm(vbow_feat)
    return normed_vbow_feat


def nearest_neighs(vbow_feat):
    N, = vbow_feat.shape
    feat = vbow_feat.reshape((1, N))
    k_nearest = model.kneighbors(feat)
    distance = k_nearest[0][0]
    k_nearest_index = k_nearest[1][0]
    rank_list = [image_order[index] for index in k_nearest_index]
    return rank_list, distance



def infer(image_path, fout_path):
    fout_folder_path = os.path.dirname(fout_path)
    if not os.path.exists(fout_folder_path):
        os.makedirs(fout_folder_path)
    if os.path.exists(fout_path):
        return
    print("Infer {}...".format(image_path))
    raw_feat = extract_features(image_path)
    normed_tf_feat = quantization(raw_feat)
    normed_vbow_feat = vbow_vectorize(normed_tf_feat, idf)
    rank_list, distance = nearest_neighs(normed_vbow_feat)
    with open(fout_path, 'w') as f:
        for i, file_path in enumerate(rank_list):
            print('{},{}'.format(file_path, distance[i]), file=f)


if __name__ == '__main__':
    for root, _, files in os.walk(args.input_folder_path):
        for f in files:
            file_name = os.path.basename(f)
            file_extension = '.' + file_name.split('.')[-1]
            image_path = os.path.join(root, f)
            fout_path = image_path.replace(args.input_folder_path, args.output_folder_path).replace(file_extension, '.txt')
            infer(image_path, fout_path)
