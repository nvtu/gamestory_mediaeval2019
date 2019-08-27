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
    # Extract rootSIFT features
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift_detector = cv2.xfeatures2d.SIFT_create()
    _, desc = sift.detectAndCompute(gray_image, None)
    eps = 1e-7
    desc /= (desc.sum(axis=1, keepdims=True) + eps)
    desc = np.sqrt(desc)
    # Feature quantization


