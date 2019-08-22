import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import os
import subprocess


def load_model():
    vbow_total_filepath = str(Path.cwd() / 'vbow_total.npy')
    vbow_total = np.load(vbow_total_filepath)
    neigh = NearestNeighbors(n_neighbors=50)
    neigh.fit(vbow_total)
    return neigh


if __name__ == '__main__':
    model = load_model()
    vbow_dir = str(Path.cwd() / 'vbow_feat')
    image_dir = str(Path.cwd() / 'LSC_DATA')
    image_order_filepath = str(Path.cwd() / 'image_path_order.txt')
    vbow_feat_filepath = os.path.join(vbow_dir, '2016-08-15', '20160815_132929_000.npy')
    image_path = vbow_feat_filepath.replace(vbow_dir, image_dir).replace('.npy', '.jpg')
    image_order = [line.rstrip() for line in open(image_order_filepath, 'r').readlines()]
    vbow_feat = np.load(vbow_feat_filepath)
    #k_nearest = model.kneighbors(vbow_feat.T, return_distance=False)
    k_nearest = model.kneighbors(vbow_feat.T)
    distance = k_nearest[0][0]
    print(distance)
    k_nearest = k_nearest[1]
    rank_list = [image_order[index] for index in k_nearest[0]]
    cmd = 'cp {} {}'.format(image_path, str(Path.cwd() / 'query'))
    subprocess.call(cmd, shell=True)
    for i, f in enumerate(rank_list):
        cmd = 'cp {} {}'.format(f, str(Path.cwd() / 'visualize' / '{}.jpg'.format(i+1))) 
        print(cmd)
        subprocess.call(cmd, shell=True)
