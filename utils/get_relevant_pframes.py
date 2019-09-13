import os
import argparse as ap
import subprocess


def create_argparse():
    parser = ap.ArgumentParser(description="Get relevant perspective frames")
    parser.add_argument('metadata_folder_path')
    parser.add_argument('perspective_frame_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


if __name__ == '__main__':
    args = create_argparse()
    if not os.path.exists(args.output_folder_path):
        os.makedirs(args.output_folder_path)
    metadata_files = [os.path.join(args.metadata_folder_path, item) for item in sorted(os.listdir(args.metadata_folder_path))]
    for file_path in metadata_files:
        content = [line.rstrip().split(',') for line in open(file_path, 'r').readlines()][0]
        pframes_folder = os.path.join(args.perspective_frame_folder_path, 'match_{}'.format(content[0]), 'round_{}'.format(content[1]))
        output_folder = os.path.join(args.output_folder_path, 'match_{}'.format(content[0]))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        cmd = 'cp -r {} {}'.format(pframes_folder, output_folder)
        print(cmd)
        subprocess.call(cmd, shell=True)




