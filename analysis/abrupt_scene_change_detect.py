import os
import argparse as ap
import cv2
import numpy as np
import subprocess


def create_argparse():
    parser = ap.ArgumentParser(description="Detect abrupt scene change")
    parser.add_argument('frame_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def compute_color_hist_diff(img1_path, img2_path):
    print(img1_path, img2_path)
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE) 
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    color_hist1 = np.bincount(img1.ravel(), minlength=256).astype(np.float32)
    color_hist1 /= np.linalg.norm(color_hist1)
    color_hist2 = np.bincount(img2.ravel(), minlength=256).astype(np.float32)
    color_hist2 /= np.linalg.norm(color_hist2)
    dist = np.sum((color_hist2 - color_hist1) ** 2)
    return dist


if __name__ == '__main__':
    args = create_argparse()
    img_paths = [os.path.join(args.frame_folder_path, item) for item in sorted(os.listdir(args.frame_folder_path))]
    num_imgs = len(img_paths)
    for i in range(1, num_imgs, 1):
        dist = compute_color_hist_diff(img_paths[i-1], img_paths[i])
        print(dist)



