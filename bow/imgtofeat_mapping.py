import os
import argparse


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for image path order and feature mapping")
    parser.add_argument('image_folder_path')
    parser.add_argument('vbow_folder_path')
    parser.add_argument('output_file_path')
    return parser.parse_args()


if __name__ == '__main__':
    args = create_argparse()
    image_paths = []
    print("Create image path order mapping...")
    for root, _, files in os.walk(args.vbow_folder_path):
        for f in files:
            original_file_name = os.path.basename(f)
            file_name = os.path.basename(f).replace('.npy', '.jpg')
            file_path = os.path.join(root, f)
            file_path = file_path.replace(args.vbow_folder_path, args.image_folder_path).replace(original_file_name, file_name)
            file_path = os.path.abspath(file_path)
            image_paths.append(file_path)
    with open(args.output_file_path, 'w') as f:
        for line in image_paths:
            print(line, file=f)
