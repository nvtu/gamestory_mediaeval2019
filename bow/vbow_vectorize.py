import numpy as np 
from pathlib import Path
import os
from multiprocessing import Process


vbow_dir = str(Path.cwd() / 'vbow_feat')
if not os.path.isdir(vbow_dir):
    os.mkdir(vbow_dir)
tf_dir = str(Path.cwd() / 'tf_feat')
image_dir = str(Path.cwd() / 'LSC_DATA')
idf_path = str(Path.cwd() / 'idf.npy')
idf = np.load(idf_path)


def vbow_create(tf_feat, idf):
    vbow_feat = tf_feat * idf
    vbow_feat = vbow_feat / np.sum(vbow_feat) # Normalize feature
    return vbow_feat


def employ_task(params):
    for p in params:
        _f, fout_path = p
        tf_feat = np.load(_f)
        vbow_feat = vbow_create(tf_feat, idf)
        np.save(fout_path, vbow_feat)


def multiprocessing_vectorize(params):
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
    # vbow feature extraction
    tf_list = []
    for root, dirs, files in os.walk(tf_dir):
        for d in dirs:
            _d = os.path.join(root, d)
            _d = _d.replace(tf_dir, vbow_dir)
            if not os.path.isdir(_d):
                os.mkdir(_d)
        for f in files:
            _f = os.path.join(root, f)
            fout_path = _f.replace(tf_dir, vbow_dir)
            if os.path.exists(fout_path): continue
            tf_list.append((_f, fout_path))
    multiprocessing_vectorize(tf_list)

    # Combine vbow feature into one file
    vbow_total = []
    vbow_total_filepath = str(Path.cwd() / 'vbow_total.npy')
    image_paths = []
    if not os.path.exists(vbow_total_filepath):
        for root, dirs, files in os.walk(vbow_dir):
            for f in files:
                _f = os.path.join(root, f)
                file_name = f.split('.')[0] + '.jpg'
                org_image_filepath = os.path.join(root.replace(vbow_dir, image_dir), file_name)
                image_paths.append(org_image_filepath)
                tf_feat = np.load(_f)            
                vbow_total.append(tf_feat.T)
        vbow_total = np.vstack(np.array(vbow_total))
        np.save(vbow_total_filepath, vbow_total)
        with open('image_path_order.txt', 'w') as f:
            for line in image_paths:
                print(line, file=f)