import numpy as np 
from pathlib import Path
import os
import argparse
import sys
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent))
from utils.exec_multiprocess import MultiProcessTask


def create_argparse():
    parser = argparse.ArgumentParser(description="Argument for vbow vectorize")
    parser.add_argument("term_freq_folder")
    parser.add_argument("idf_file_path")
    parser.add_argument("output_folder_path")
    return parser.parse_args()


args = create_argparse()
idf = np.load(args.idf_file_path)


def create_params(args):
    print("Creating params vbow vectorization...")
    params = []
    output_folder_path = os.path.join(args.output_folder_path, 'vbow')
    for root, _, files in os.walk(args.term_freq_folder):
        for f in files:
            file_path = os.path.join(root, f)
            output_file_path = file_path.replace(args.term_freq_folder, output_folder_path)
            params.append([file_path, output_file_path])
    return params


def vbow_create(p):
    file_path, output_file_path = p
    output_dir_path = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    if os.path.exists(output_file_path):
        return
    print("BOVW vectorize {}...".format(file_path))
    tf_feat = np.load(file_path)
    vbow_feat = tf_feat * idf
    normed_vbow_feat = vbow_feat / np.linalg.norm(vbow_feat)
    np.save(output_file_path, normed_vbow_feat)


def combine_vbow_into_one_file(vbow_folder_path):
    vbow_total = []
    for root, _, files in os.walk(vbow_folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            feat = np.load(file_path)
            vbow_total.append(feat)
    vbow_total = np.vstack(np.array(vbow_total))        
    return vbow_total



if __name__ == '__main__':
    # vbow feature extraction
    params = create_params(args)
    mtp = MultiProcessTask(params, vbow_create)
    mtp.run_multiprocess()

    # Combine vbow feature into one file
    vbow_total = []
    vbow_total_filepath = os.path.join(args.output_folder_path, 'vbow_total.npy')
    vbow_folder_path = os.path.join(args.output_folder_path, 'vbow')
    if not os.path.exists(vbow_total_filepath):
        vbow_total = combine_vbow_into_one_file(vbow_folder_path)
        np.save(vbow_total_filepath, vbow_total)
