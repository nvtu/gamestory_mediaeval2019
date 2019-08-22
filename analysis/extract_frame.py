import os
import sys
import subprocess
import argparse
from pathlib import Path
sys.path.append(str(Path(os.getcwd())))
from utils.time_utils import time_this
from utils.exec_multiprocess import MultiProcessTask


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for video frame extraction")
    parser.add_argument("video_match_folder_path")
    parser.add_argument("output_frame_folder")
    return parser.parse_args()


@time_this
def run_extract_frame(p):
    video_path, output_folder = p
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        return
    cmd = "ffmpeg -i {} -f image2 -vf fps=1 {}/%6d.jpg".format(video_path, output_folder)
    print(cmd)
    subprocess.call(cmd, shell=True)


@time_this
def create_params(args):
    params = []
    matches = os.listdir(args.video_match_folder_path)
    matches = sorted(matches, key=lambda x: int(x.split('_')[-1]))
    for match in matches:
        match_folder_path = os.path.join(args.video_match_folder_path, match)
        rounds = os.listdir(match_folder_path)
        rounds = sorted(rounds, key=lambda x: int(x.split('_')[-1]))
        for round in rounds:
            round_folder_path = os.path.join(match_folder_path, round, 'video')
            videos = os.listdir(round_folder_path)
            videos = sorted(videos, key=lambda x: int(x.split('_')[-1].split('.')[0][1:]))
            for video in videos:
                video_name = video.split('.')[0]
                video_path = os.path.join(round_folder_path, video)
                output_folder = os.path.join(args.output_frame_folder, match, round, video_name)
                params.append([video_path, output_folder])
    return params


if __name__ == '__main__':
    args = create_argparse()
    params = create_params(args)
    mtp = MultiProcessTask(params, run_extract_frame)
    mtp.run_multiprocess()
