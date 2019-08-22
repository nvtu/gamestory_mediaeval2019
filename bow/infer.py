from extract_features import gen_sift_features, to_gray
from quantization import generate_term_freq
from vbow_vectorize import vbow_create
from pathlib import Path
from nearest_neighbor import load_model, nearest_neighs
from sklearn.externals import joblib
import numpy as np
import cv2
import os



kmeans_storage = joblib.load(str(Path.cwd() / 'kmeans_cluster.storage'))
idf = np.load(str(Path.cwd() / 'idf.npy'))
model = load_model()
image_order_filepath = str(Path.cwd() / 'image_path_order.txt')
image_order = [line.rstrip() for line in open(image_order_filepath, 'r').readlines()]


def infer(image_path, fout_path):
    image = cv2.imread(image_path)
    gray_image = to_gray(image)
    _, desc = gen_sift_features(gray_image)
    tf_feat = generate_term_freq(desc, kmeans_storage)
    vbow_feat = vbow_create(tf_feat, idf)
    rank_list, distance = nearest_neighs(vbow_feat)
    with open(fout_path, 'w') as f:
        for i, file_path in enumerate(rank_list):
            print(file_path, file=f)


if __name__ == '__main__':
    query_dir = str(Path.cwd() / 'puzzle_test')
    output_dir = str(Path.cwd() / 'puzzle_result')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for root, dirs, files in os.walk(query_dir):
        for d in dirs:
            _d = os.path.join(root, d)
            _d = _d.replace(query_dir, output_dir)
            if not os.path.isdir(_d):
                os.mkdir(_d)
        for f in files:
            file_name, ext = f.split('.')
            print(ext)
            if ext != 'JPG' and ext != 'jpg': continue
            _f = os.path.join(root, f)
            fout_path = _f.replace(query_dir, output_dir).replace('.'+ext, '.txt')
            if not os.path.exists(fout_path):
                print(fout_path)
                infer(_f, fout_path)


