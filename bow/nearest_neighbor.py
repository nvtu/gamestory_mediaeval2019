import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import os
import sys
import subprocess
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent))
from utils.exec_multiprocess import MultiProcessTask
import argparse


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for nearest neighbor search")
    parser.add_argument('vbow_total_file_path')
    parser.add_argument('image_path_order_file_path')
    parser.add_argument('input_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def load_model(vbow_total_filepath):
    print("Loading knn model...")
    vbow_total = np.load(vbow_total_filepath)
    neigh = NearestNeighbors(n_neighbors=1000)
    neigh.fit(vbow_total)
    return neigh


def load_image_path_order(image_path_order_filepath):
    print("Loading image path order...")
    image_path_order = [line.rstrip() for line in open(image_path_order_filepath, 'r').readlines()]
    return image_path_order


args = create_argparse()
model = load_model(args.vbow_total_file_path)
image_order = load_image_path_order(args.image_path_order_file_path)


def create_params(args):
    print("Creating params for nearest neighbor search...")
    params = []
    for root, _, files in os.walk(args.input_folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            output_file_name = f.replace('.npy', '.txt')
            output_file_path = file_path.replace(args.input_folder_path, args.output_folder_path)
            output_file_path = output_file_path.replace(f, output_file_name)
            params.append([file_path, output_file_path])
    return params


def nearest_neighs(vbow_feat):
    N, = vbow_feat.shape
    feat = vbow_feat.reshape((1, N))
    k_nearest = model.kneighbors(feat)
    distance = k_nearest[0][0] 
    k_nearest_index = k_nearest[1][0]
    rank_list = [image_order[index] for index in k_nearest_index]
    return rank_list, distance


def run_nnsearch(p):
    file_path, output_file_path = p
    output_dir_path = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    if os.path.exists(output_file_path):
        return
    print("Processing {}...".format(file_path))
    vbow_feat = np.load(file_path)
    rank_list, distance = nearest_neighs(vbow_feat)
    with open(output_file_path, 'w') as f:
        for i, file_path in enumerate(rank_list):
            print('{},{}'.format(file_path, distance[i]), file=f)


if __name__ == '__main__':
    params = create_params(args) 
    mtp = MultiProcessTask(params, run_nnsearch)
    mtp.run_multiprocess()
