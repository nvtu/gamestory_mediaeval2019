import pandas as pd
import os
import subprocess
import argparse


def create_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('ground_truth_metadata')
    parser.add_argument('video_file_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def extract_groundtruth_videos(args):
    df = pd.read_csv(args.ground_truth_metadata, delimiter=';')
    fps = 59
    if not os.path.exists(args.output_folder_path):
        os.makedirs(args.output_folder_path)
    for v in df.values:
        _, replay_start, replay_end, *r = v
        replay_start_second = replay_start / fps
        replay_end_second = replay_end / fps
        extend_sec = 0
        extend_replay_start = replay_start_second - extend_sec
        extend_replay_end = replay_end_second + extend_sec
        duration = extend_replay_end - extend_replay_start
        output_file_path = os.path.join(args.output_folder_path, '{}.mp4'.format(int(replay_start_second)))
        cmd = 'ffmpeg -ss {} -vsync 1 -i {} -strict -2 -t {} -c copy {}'.format(extend_replay_start, args.video_file_path, duration, output_file_path)
        print(cmd)
        subprocess.call(cmd, shell=True)



if __name__ == '__main__':
    args = create_argparse()
    extract_groundtruth_videos(args)

