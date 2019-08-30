import cv2
import os
import argparse as ap


def create_argparse():
    parser = ap.ArgumentParser(description="Arguments for image cropping")
    parser.add_argument('image_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


if __name__ == '__main__':
    args = create_argparse()
    for root, _, files in os.walk(args.image_folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            image = cv2.imread(file_path)
            cropped_image = image[112:243, :]
            output_file_path = file_path.replace(args.image_folder_path, args.output_folder_path)
            output_folder_path = os.path.dirname(output_file_path)
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)
            cv2.imwrite(output_file_path, cropped_image)
