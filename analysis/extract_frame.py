import os
import subprocess
import argparse
from pathlib import Path
from utils.time_utils import time_this


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments for video frame extraction")
    parser.add_argument("video_folder_path")
    parser.add_argument("output_video_path")
    return parser.parse_args()


@time_this
def extract_frame(video_path):
    cmd = "ffmpeg -i {} -vcodec png -r 1 -an -f image2 {}/frame_test/%6d.png".format(video_path, str(Path(os.getcwd()).parent))
    print(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    video_filepath = str(Path(os.getcwd()).parent / 'training' / '2018-03-02_P1.mp4')
    print(video_filepath)
    extract_frame(video_filepath)
