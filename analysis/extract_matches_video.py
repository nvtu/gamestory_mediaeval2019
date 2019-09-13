import os
import sys
from pathlib import Path
sys.path.append(str(Path(os.getcwd())))
import argparse
import pandas as pd
import json
import subprocess
from utils.time_utils import round_time, round_datetime, to_standard_ffmpeg_format



def create_argparse():
    parser = argparse.ArgumentParser(description = "Arguments for extracting video for each match")
    parser.add_argument('video_folder_path')
    parser.add_argument('matches_metadata_folder_path')
    parser.add_argument('gameplay_metadata_file_path')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def create_params(args):
    # time_deviation = [36, 31, 34, 33, 30, 33, 33, 32, 33, 34] # magic numbers for train videos
    time_deviation = [36, 37, 38, 37, 39, 35, 38, 38, 37, 39] # magic numbers for test videos
    print("Creating necessary parameters to cut videos...")
    params = []
    df = pd.read_csv(args.gameplay_metadata_file_path)
    gameplay_metadata = [v for v in df.values if v[5] != 'P11' and v[5] != 'P12' and v[3] != 'highlight' and int(v[2]) > 100]
    matches = os.listdir(args.matches_metadata_folder_path)
    matches = sorted(matches, key=lambda x: int(x.split('_')[-1]))
    for i, match in enumerate(matches):
        match_folder_path = os.path.join(args.matches_metadata_folder_path, match)
        rounds = os.listdir(match_folder_path)
        rounds = sorted(rounds, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        match_metadata = [item[4:] for item in gameplay_metadata if item[4] == i+1]
        match_metadata = sorted(match_metadata, key=lambda x: int(x[1][1:]))
        num_perspective = match_metadata.__len__()
        for j in range(num_perspective):
            metadata = match_metadata[j]
            video_name = metadata[2]
            video_filepath = os.path.join(args.video_folder_path, video_name)
            initial_stream_time = round_time(metadata[3])
            initial_UTC_time = round_datetime(metadata[4].replace(' ', 'T'))
            for round in rounds:
                round_file_path = os.path.join(match_folder_path, round)
                round_info = json.load(open(round_file_path, 'r'))
                start_time = round_datetime(round_info['start_time']) # It is in UTC time
                end_time = round_datetime(round_info['end_time'], round_upper=True) # It is in UTC time
                seek_time = (start_time - initial_UTC_time + initial_stream_time).total_seconds() + time_deviation[j]
                to_time = (end_time - initial_UTC_time + initial_stream_time).total_seconds() + time_deviation[j] + 1
                # Create output file path of cut-videos
                # The hierarchy would be like this:
                # match_videos
                #   |__match_{$id}
                #       |__ round_{$id}
                #           |__ video
                #               |__ video_name 
                #           |__ metadata
                #               |__ metadata_name 
                output_folder = os.path.join(args.output_folder_path, 'match_{}'.format(i+1), 'round_{}'.format(round_info['round_idx']))
                output_video_filepath = os.path.join(output_folder, 'video', video_name)
                output_metadata_filepath = os.path.join(output_folder, 'metadata', video_name.split('.')[0] + '.csv')
                params.append([video_filepath, output_video_filepath, output_metadata_filepath, seek_time, to_time])
    return params


def run_cut_video(p):
    """
    - p is an item in the list params in create_params function
    """
    video_filepath, output_video_filepath, output_metadata_filepath, seek_time, to_time = p
    if os.path.exists(output_video_filepath) and os.path.exists(output_metadata_filepath):
        # ignore processed files
        return
    output_video_folder = str(Path(output_video_filepath).parent)
    output_metadata_folder = str(Path(output_metadata_filepath).parent)
    if not os.path.exists(output_video_folder):
        os.makedirs(output_video_folder)
    if not os.path.exists(output_metadata_folder):
        os.makedirs(output_metadata_folder)
    with open(output_metadata_filepath, 'w') as f:
        f.write('start_time, end_time, start_second, end_second\n')
        f.write('{},{},{},{}'.format(to_standard_ffmpeg_format(seek_time), to_standard_ffmpeg_format(to_time), seek_time, to_time))
    delta_time = to_time - seek_time
    seek_time = to_standard_ffmpeg_format(seek_time)
    delta_time = to_standard_ffmpeg_format(delta_time)
    cmd = 'ffmpeg -ss {} -vsync 1 -i {} -strict -2 -t {} -c copy {}'.format(seek_time, video_filepath, delta_time, output_video_filepath)
    print(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    args = create_argparse()
    params = create_params(args)
    for p in params:
        print(p)
        #run_cut_video(p)
        # exit(0)
