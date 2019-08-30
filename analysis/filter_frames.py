import argparse as ap
import os
import cv2
import numpy as np
import subprocess


def create_argparse():
    parser = ap.ArgumentParser()
    parser.add_argument('frames_folder_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def compute_color_hist_diff(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE) 
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    color_hist1 = np.bincount(img1.ravel(), minlength=256).astype(np.float32)
    color_hist1 /= np.linalg.norm(color_hist1)
    color_hist2 = np.bincount(img2.ravel(), minlength=256).astype(np.float32)
    color_hist2 /= np.linalg.norm(color_hist2)
    dist = np.sum((color_hist2 - color_hist1) ** 2)
    return dist


def compute_orb_diff(img1_path, img2_path):
    print(img1_path, img2_path)
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE) 
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    orb = cv2.ORB_create()
    kp1, desc1 = orb.detectAndCompute(img1, None)
    kp2, desc2 = orb.detectAndCompute(img2, None)
    if desc1 is None or desc2 is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc1, desc2)
    matches = sorted(matches, key=lambda x: x.distance)
    return len(matches)


def copy_image(source_path, output_path):
    cmd = 'cp {} {}'.format(source_path, output_path)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    args = create_argparse()
    if not os.path.exists(args.output_folder_path):
        os.makedirs(args.output_folder_path)
    frame_paths = [os.path.join(args.frames_folder_path, item) for item in sorted(os.listdir(args.frames_folder_path))]
    num_frames = len(frame_paths)
    color_diff_threshold = 0.2
    bf_match_threshold = 300
    i = 0
    j = 1
    while i < num_frames:
       while j < num_frames:
            dist = compute_color_hist_diff(frame_paths[i], frame_paths[j])
            num_matches = compute_orb_diff(frame_paths[i], frame_paths[j])
            print('Difference score between {}-frame and {}-frame: {} - {} matches'.format(i+1, j+1, dist, num_matches))
            if dist < color_diff_threshold or num_matches > bf_match_threshold:
                j += 1
            else:
                output_file_path = frame_paths[i].replace(args.frames_folder_path, args.output_folder_path)
                copy_image(frame_paths[i], output_file_path)
                i = j
                j += 1
                break
        if i == num_frames - 1 or j == num_frames:
            output_file_path = frame_paths[i].replace(args.frame_folder_path, args.output_folder_path)
            copy_image(frame_paths[i], output_file_path)
            exit(0)
 
