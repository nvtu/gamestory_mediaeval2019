import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import os
import subprocess
from multiprocessing import Process


def load_model():
    vbow_total_filepath = str(Path.cwd() / 'vbow_total.npy')
    vbow_total = np.load(vbow_total_filepath)
    neigh = NearestNeighbors(n_neighbors=200)
    neigh.fit(vbow_total)
    return neigh


model = load_model()
image_order_filepath = str(Path.cwd() / 'image_path_order.txt')
image_order = [line.rstrip() for line in open(image_order_filepath, 'r').readlines()]
image_dir = str(Path.cwd() / 'LSC_DATA')


def nearest_neighs(vbow_feat):
    k_nearest = model.kneighbors(vbow_feat.T)
    distance = k_nearest[0][0] 
    k_nearest_index = k_nearest[1][0]
    rank_list = [image_order[index] for index in k_nearest_index]
    return rank_list, distance


def employ_task(params):
    for p in params:
        _f, fout_path = p
        print('Processing {}'.format(_f))
        vbow_feat = np.load(_f)
        rank_list, distance = nearest_neighs(vbow_feat)
        with open(fout_path, 'w') as f:
            for i, file_path in enumerate(rank_list):
                print('{},{}'.format(file_path, distance[i]), file=f)


def multiprocess_infer(params):
    num_processes = 20
    task_per_process = len(params) // num_processes + 1
    tasks = []
    for i in range(num_processes):
        sub_p = params[i * task_per_process : min((i+1) * task_per_process, len(params))]
        tasks.append(Process(target=employ_task, args=(sub_p,)))
        tasks[-1].start()
    for t in tasks:
        t.join()


if __name__ == '__main__':
    vbow_dir = str(Path.cwd() / 'vbow_feat')
    vbow_result_dir = str(Path.cwd() / 'vbow_result')
    if not os.path.isdir(vbow_result_dir):
        os.mkdir(vbow_result_dir)
    vbow_feats = []
    for root, dirs, files in os.walk(vbow_dir):
        for d in dirs:
            _d = os.path.join(root, d).replace(vbow_dir, vbow_result_dir)
            if not os.path.isdir(_d):
                os.mkdir(_d)
        
        for f in files:
            _f = os.path.join(root, f)
            fout_path = _f.replace(vbow_dir, vbow_result_dir).replace('.npy', '.txt')
            if os.path.exists(fout_path): continue
            vbow_feats.append((_f, fout_path))
    multiprocess_infer(vbow_feats)

    # vbow_feat_filepath = os.path.join(vbow_dir, '2016-08-23', '20160823_062708_000.npy')
    # vbow_feat = np.load(vbow_feat_filepath)
    # image_path = vbow_feat_filepath.replace(vbow_dir, image_dir).replace('.npy', '.jpg')
    # k_nearest = model.kneighbors(vbow_feat.T, return_distance=False)
    # rank_list = [image_order[index] for index in k_nearest[0]]
    # cmd = 'cp {} {}'.format(image_path, str(Path.cwd() / 'query'))
    # subprocess.call(cmd, shell=True)
    # for f in rank_list:
    #     cmd = 'cp {} {}'.format(f, str(Path.cwd() / 'visualize')) 
    #     print(cmd)
    #     subprocess.call(cmd, shell=True)
