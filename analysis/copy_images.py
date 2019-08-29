import os
import argparse as ap
import subprocess
import shutil


def create_argparse():
    parser = ap.ArgumentParser()
    parser.add_argument('result_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def copy_result_images(rank_list_file_path, output_folder_path):
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.makedirs(output_folder_path)
    print("Processing {}...".format(rank_list_file_path))
    content = [line.rstrip().split(',') for line in open(rank_list_file_path, 'r').readlines()]
    for i, c in enumerate(content):
        file_path, score = c
        file_name = os.path.basename(file_path)
        #output_file_path = os.path.join(output_folder_path, '{:03d}_{}'.format(i+1, file_name))
        output_file_path = os.path.join(output_folder_path, '{}'.format(file_name))
        if float(score) <= 1.0:
            cmd = 'cp {} {}'.format(file_path, output_file_path)
            subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    args = create_argparse()
    for root, _, files in os.walk(args.result_folder_path):
        for f in files:
            file_name = os.path.basename(f).split('.')[0]
            rank_list_file_path = os.path.join(root, f)
            output_folder_path = os.path.join(args.output_folder_path, file_name)
            copy_result_images(rank_list_file_path, output_folder_path)
