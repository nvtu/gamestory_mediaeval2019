import os
import numpy as np
import argparse as ap
import subprocess
import pandas as pd
from collections import Counter


def create_argparse():
    parser = ap.ArgumentParser(description="Argument for multistream synchronization between player perspective and replay videos")
    parser.add_argument('perspective_rank_list_folder')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def delete_empty_files(perspective_rank_list_folder):
    for root, _, files in os.walk(perspective_rank_list_folder):
        for f in files:
            file_path = os.path.join(root, f)
            content = [line.rsplit() for line in open(file_path, 'r').readlines()]
            if content.__len__() == 0:
                print("Removing empty files {}".format(file_path))
                cmd = 'rm {}'.format(file_path)
                subprocess.call(cmd, shell=True)


def combine_rank_list(perspective_rank_list_folder):
    rank_list_folders = sorted(os.listdir(perspective_rank_list_folder))
    for folder_name in rank_list_folders:
        folder_path = os.path.join(perspective_rank_list_folder, folder_name)
        combined_list = []
        perspective_choice_list = []
        remaining_files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0]))
        print(folder_path)
        for f in remaining_files:
            file_path = os.path.join(folder_path, f)
            df = pd.read_csv(file_path)
            raw_rank_list = [item[0] for item in df.values]
            adjusted_rank_list = [item.split('/')[-2:] for item in raw_rank_list]
            perspective_choice = [item[0] for item in adjusted_rank_list]
            perspective_choice_list += perspective_choice
            # combined_list += adjusted_rank_list
        cnt = Counter(perspective_choice_list)
        print(cnt)


if __name__ == '__main__':
    args = create_argparse()
    delete_empty_files(args.perspective_rank_list_folder)
    combine_rank_list(args.perspective_rank_list_folder)