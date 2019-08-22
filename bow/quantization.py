from sklearn.externals import joblib
from pathlib import Path
import os
from multiprocessing import Process
import numpy as np
from collections import Counter, defaultdict
import math


tf_dir = str(Path.cwd() / 'tf_feat')
sift_feat = str(Path.cwd() / 'sift_feat')
if not os.path.isdir(tf_dir):
    os.mkdir(tf_dir)
kmeans_storage = joblib.load('kmeans_cluster.storage')
num_cluster = len(kmeans_storage.cluster_centers_)


def generate_term_freq(sift_feat, kmeans_storage):
    preds = kmeans_storage.predict(sift_feat)
    tf_dict = Counter(preds)
    term_freq = np.zeros((num_cluster, 1))
    mmax = 0
    for key, freq in tf_dict.items():
        term_freq[key] = freq
        mmax = max(mmax, freq)
    term_freq = term_freq / mmax
    return term_freq


def generate_idf(total_images, tf_total):
    idf = np.zeros((num_cluster, 1))
    for i in range(num_cluster):
        n_qi = np.where(tf_total[:, i] > 0)[0].shape[0]
        idf[i] = math.log(total_images / n_qi)
    return idf


def employ_task(params):
    for p in params:
        _f, fout_path = p
        print(fout_path)
        sift_feat = np.load(_f)
        term_freq = generate_term_freq(sift_feat, kmeans_storage)
        np.save(fout_path, term_freq)


def multiprocess_quantize(params):
    num_processes = 20
    task_per_process = len(params) // num_processes + 1
    tasks = []
    for i in range(num_processes):
        sub_p = params[i * task_per_process : min((i + 1) * task_per_process, len(params))]
        tasks.append(Process(target=employ_task, args=(sub_p,)))
        tasks[-1].start()
    for task in tasks:
        task.join()


if __name__ == '__main__':
    total_images = 0

    # Create tf vector
    sift_flist = []
    for root, dirs, files in os.walk(sift_feat):
        for d in dirs:
            _d = os.path.join(root, d)
            _d = _d.replace(sift_feat, tf_dir)
            if not os.path.isdir(_d):
                os.mkdir(_d)
        total_images += len(files)
        for f in files:
            _f = os.path.join(root, f)
            fout_path = _f.replace(sift_feat, tf_dir)
            if os.path.exists(fout_path): continue
            sift_flist.append((_f, fout_path))
    multiprocess_quantize(sift_flist)

    # Create idf vector
    tf_feat_filepath = str(Path.cwd() / 'term_freq_total.npy')
    term_freq_total = []
    if not os.path.exists(tf_feat_filepath):
        for root, dirs, files in os.walk(tf_dir):
            for f in files:
                _f = os.path.join(root, f)
                term_freq = np.load(_f)
                term_freq_total.append(term_freq.T)
        term_freq_total = np.vstack(np.array(term_freq_total))
        np.save(tf_feat_filepath, term_freq_total)
    idf_filepath = str(Path.cwd() / 'idf.npy')
    if os.path.exists(idf_filepath): exit(0)
    term_freq_total = np.load(tf_feat_filepath)
    idf = generate_idf(total_images, term_freq_total)
    np.save(idf_filepath, idf)