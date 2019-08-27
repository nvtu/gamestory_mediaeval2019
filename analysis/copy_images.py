import os
import argparse as ap
import subprocess


def create_argparse():
    parser = ap.ArgumentParser()
    parser.add_argument('rank_list_file_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


if __name__ == '__main__':
    args = create_argparse()
    content = [line.rstrip().split(',') for line in open(args.rank_list_file_path, 'r').readlines()]
    for i, c in enumerate(content):
        file_path, score = c
        file_name = os.path.basename(file_path)
        if float(score) <= 1.0:
            cmd = 'cp {} {}'.format(file_path, os.path.join(args.output_folder_path, file_name))
            print(cmd)
            subprocess.call(cmd, shell=True)
