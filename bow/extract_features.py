import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from multiprocessing import Process
import os
import subprocess
import argparse
sys.path.append(str(Path(os.getcwd())))
from utils.exec_multiprocess import MultiProcessTask


"""
Extract RootSift features from image - One can convert it back to extract SIFT feature by commenting line.
The structure of output folder will be like this:
    |__ output_rootsift_feat_folder
        |
        |__ rootsift_feat
            | 
            |__ image_name.npy (The feature file will be named after its corresponding origin image)
        |
        |__ combined_rootsift_feat.npy
"""

def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for RootSIFT feature extraction")
    parser.add_argument('dataset_folder')
    parser.add_argument('output_rootsift_feat_folder')
    return parser.parse_args()


def create_params(args):
    print("Preparing parameters for rootSIFT feature extraction...")
    params = []
    rootsift_feat_folder = os.path.join(args.output_rootsift_feat_folder, 'rootsift_feat')
    for root, _, files in os.walk(args.dataset_folder):
        for f in files:
            file_path = os.path.join(root, f)
            fout_path = file_path.replace(args.dataset_folder, rootsift_feat_folder)
            output_file_name = f.split('.')[0] + '.npy'
            fout_path = fout_path.replace(f, output_file_name)
            params.append([file_path, fout_path])
    return params
    
    
def extract_root_sift_feat(p):
    file_path, fout_path = p
    fout_folder_path = os.path.dirname(fout_path)
    if not os.path.exists(fout_folder_path):
        os.makedirs(fout_folder_path)
    if os.path.exists(fout_path):
        return
    print("Extracting rootSIFT features of image %s" % file_path)
    # Read image and convert to gray scale image to extract SIFT features
    color_img = cv2.imread(file_path)
    gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
    # Extract SIFT feature
    sift = cv2.xfeatures2d.SIFT_create()
    kp, desc = sift.detectAndCompute(gray_img, None)
    # Check if image has SIFT descriptor
    if isinstance(desc, type(None)):
        return
    # Create RootSIFT feature
    eps = 1e-7
    desc /= (desc.sum(axis=1, keepdims=True) + eps)
    desc = np.sqrt(desc)
    # Save SIFT descriptor
    np.save(fout_path, desc)


def combine_feat_into_one_file(rootsift_folder_path, output_filepath):
    if not os.path.exists(rootsift_folder_path):
        print("Please extract root sift features first before combining them")
        return
    if os.path.exists(output_filepath):
        print("RootSIFT features were combined")
        return
    print("Combining RootSIFT features into one file")
    combined_feats = []
    for root, _, files in os.walk(rootsift_folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            feat = np.load(file_path)
            combined_feats.append(feat)
    combined_feats = np.vstack(np.array(combined_feats))
    np.save(output_filepath, combined_feats)

    
#def show_sift_features(gray_img, color_img, kp):
#    return plt.imshow(cv2.drawKeypoints(gray_img, kp, color_img.copy()))


if __name__ == '__main__':
    args = create_argparse()
    params = create_params(args)
    mpt = MultiProcessTask(params, extract_root_sift_feat)
    mpt.run_multiprocess()
    # Combine rootsift features into one file
    rootsift_feat_folder = os.path.join(args.output_rootsift_feat_folder, 'rootsift_feat')
    combined_feats_filepath = os.path.join(args.output_rootsift_feat_folder, 'combined_rootsift_feat.npy')
    combine_feat_into_one_file(rootsift_feat_folder, combined_feats_filepath)
