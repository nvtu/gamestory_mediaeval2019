import os
import argparse as ap
import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors


def create_argparse():
    parser = ap.ArgumentParser(description="")
    parser.add_argument('image_path')
    parser.add_argument('frame_folder_path')
    parser.add_argument('output_file_path')
    return parser.parse_args()


def extract_color_histogram(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    color_hist = np.bincount(img.ravel(), minlength=256).astype(np.float32)
    color_hist /= np.linalg.norm(color_hist)
    return color_hist


if __name__ == '__main__':
    args = create_argparse()
    perspective_folders = [os.path.join(args.frame_folder_path, item) for item in sorted(os.listdir(args.frame_folder_path), key=lambda x: int(x.split('_')[-1].split('P')[-1]))]
    img_paths = []
    for p in perspective_folders:
        img_lists = [os.path.join(p, item) for item in sorted(os.listdir(p))]
        img_paths += img_lists
    color_hist_lists = []
    for img_path in img_paths:
        color_hist = extract_color_histogram(img_path)
        color_hist_lists.append(color_hist)
    color_hist_lists = np.vstack(np.array(color_hist_lists))
    query_color_hist = extract_color_histogram(args.image_path)
    query_color_hist = query_color_hist.reshape((1, 256))
    model = NearestNeighbors(n_neighbors=5)
    model.fit(color_hist_lists)
    kneighbors = model.kneighbors(query_color_hist)
    distance = kneighbors[0][0]
    knearest_index = kneighbors[1][0]
    rank_list = [img_paths[index] for index in knearest_index]
    print(rank_list)
    print(distance)



