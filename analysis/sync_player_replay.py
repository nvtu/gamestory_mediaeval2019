import os
import numpy as np
import argparse as ap
import subprocess
import pandas as pd
from collections import Counter
import json
import shutil


replay_fps = 59
perspective_fps = 60
original_P11_video = '/Users/tuninh/DCU/MediaEval2019/GameStory/2018-03-03_P11.mp4'

def create_argparse():
    parser = ap.ArgumentParser(description="Argument for multistream synchronization between player perspective and replay videos")
    parser.add_argument('replay_video_folder_path')
    parser.add_argument('replay_metadata_folder_path')
    parser.add_argument('matches_videos_folder_path')
    parser.add_argument('perspective_rank_list_folder')
    parser.add_argument('output_folder_path')
    return parser.parse_args()


def delete_empty_files(perspective_rank_list_folder):
    for root, _, files in os.walk(perspective_rank_list_folder):
        for f in files:
            file_path = os.path.join(root, f)
            # content = [line.rsplit() for line in open(file_path, 'r').readlines()]
            content = json.load(open(file_path, 'r'))
            if content.__len__() == 0:
                print("Removing empty files {}".format(file_path))
                cmd = 'rm {}'.format(file_path)
                subprocess.call(cmd, shell=True)


def get_replay_start_frame(replay_vid_name):
    start_frame, _ = replay_vid_name.split('_')
    return int(start_frame)


def get_perspective_start_frame(perspective_metadata_file_path):
    df = pd.read_csv(perspective_metadata_file_path)
    start_second = int(df.values[0][2])
    start_frame = start_second * replay_fps
    return start_frame


def detect_replay_and_sync_multistream(args):
    replay_videos = [os.path.join(args.perspective_rank_list_folder, item) for item in sorted(os.listdir(args.perspective_rank_list_folder))]
    results = []
    for vid in replay_videos:
        print(vid)
        similar_matching_files = [os.path.join(vid, item) for item in sorted(os.listdir(vid))]
        if similar_matching_files.__len__() == 0:
            continue
        player_perspective = []
        timelines = []
        match_idxs = []
        round_idxs = []
        for f in similar_matching_files:
            content = json.load(open(f, 'r'))
            most_similar = content[0]['path']
            match_idx, round_idx, perspective, image_name = most_similar.split('/')[-4:]
            match_idxs.append(match_idx)
            round_idxs.append(round_idx)
            player_perspective.append(perspective)
            timelines.append(int(image_name.split('.')[0]))
        timelines.append(1e18) # Add redundant infinite boundary
        player_view_histogram = Counter(player_perspective) 
        print(player_view_histogram)
        player_perspective.append(player_perspective[-1])
        num_moments = len(timelines)
        replay_lists = []
        checkpoint = 0
        
        # Refine time frames
        # refined_timelines = [timelines[0]]
        # for i in range(1, num_moments):
        #     most_common = Counter(timelines[i-1:i+2]).most_common()[0]
        #     if most_common[1] > 1:
        #         refined_timelines.append(most_common[0])
        #     else:
        #         refined_timelines.append(timelines[i])
        # timelines = refined_timelines
        # timelines.append(1e18)

        # Detect scene change based on retrieved time frame
        vid_name = vid.split('/')[-1].split('.')[0]
        video_file_path = os.path.join(args.replay_video_folder_path, vid_name + '.mp4')
        video_output_folder_path = os.path.join(args.output_folder_path, 'final_replay_videos', vid_name)
        origin_video_folder_path = os.path.join(args.output_folder_path, 'origin_replay_videos', vid_name)
        perspective_video_folder_path = os.path.join(args.output_folder_path, 'perspective_replay_videos', vid_name)
        if not os.path.exists(video_output_folder_path):
            os.makedirs(video_output_folder_path)
        if not os.path.exists(origin_video_folder_path):
            os.makedirs(origin_video_folder_path)
        if not os.path.exists(perspective_video_folder_path):
            os.makedirs(perspective_video_folder_path)
 
        cnt = 0
        for i in range(1, num_moments):
            delta_time = abs(timelines[i] / replay_fps - timelines[i-1] / replay_fps)
            replay_delta_time = abs(timelines[i-1] / replay_fps - timelines[checkpoint] / replay_fps)
            if (delta_time > 3.5 and replay_delta_time >= 1.1) or (player_perspective[i] != player_perspective[i-1] and player_view_histogram[player_perspective[i]] > 30):
                print(delta_time, replay_delta_time)
                cnt += 1
                # print(delta_time, replay_delta_time)
                sorted_timelines = sorted(timelines[checkpoint:i])
                replay_start_frame = int(similar_matching_files[checkpoint].split('/')[-1].split('.')[0]) + get_replay_start_frame(vid_name)
                replay_end_frame = int(similar_matching_files[i-1].split('/')[-1].split('.')[0]) + get_replay_start_frame(vid_name)
                perspective = player_perspective[i-1].split('-')[-1]
                perspective_metadata_file_path = os.path.join(args.matches_videos_folder_path, match_idxs[i-1], round_idxs[i-1], 'metadata', player_perspective[i-1] + '.csv')
                perspective_origin_start_frame = get_perspective_start_frame(perspective_metadata_file_path)

                # Main video replay sub-videos
                start_time = (replay_start_frame - get_replay_start_frame(vid_name)) / replay_fps
                end_time = (replay_end_frame - get_replay_start_frame(vid_name)) / replay_fps
                delta_time = end_time - start_time
                output_video_file_path = os.path.join(video_output_folder_path, '{:03d}.mp4'.format(cnt))
                replay_video_extract_cmd = 'ffmpeg -ss {} -i {} -vsync 1 -strict -2 -t {} -c copy {}'.format(start_time, video_file_path, delta_time, output_video_file_path)

                # Perspective player sub-videos
                perspective_start_frame = sorted_timelines[0] + perspective_origin_start_frame
                perspective_end_frame = int(perspective_start_frame + delta_time * perspective_fps)
                perspective_start_time = sorted_timelines[0] / perspective_fps
                perspective_delta_time = (perspective_end_frame - perspective_start_frame) / perspective_fps 
                perspective_video_path = os.path.join(args.matches_videos_folder_path, match_idxs[i-1], round_idxs[i-1], 'video', player_perspective[i-1] + '.mp4')
                perspective_output_video_path = os.path.join(perspective_video_folder_path, '{:03d}.mp4'.format(cnt))
                perspective_video_extract_cmd = 'ffmpeg -ss {} -i {} -vsync 1 -strict -2 -t {} -c copy {}'.format(perspective_start_time, perspective_video_path,
                    perspective_delta_time, perspective_output_video_path)
            
                # Origin video replay sub-videos
                origin_start_time = replay_start_frame / replay_fps
                origin_end_time = replay_end_frame / replay_fps
                origin_delta_time = origin_end_time - origin_start_time
                origin_output_video_file_path = os.path.join(origin_video_folder_path, '{:03d}.mp4'.format(cnt))
                origin_video_extract_cmd = 'ffmpeg -ss {} -i {} -vsync 1 -strict -2 -t {} -c copy {}'.format(origin_start_time, original_P11_video, origin_delta_time, origin_output_video_file_path)

                replay_lists.append((replay_start_frame, replay_end_frame, perspective_start_frame, perspective_end_frame, 
                    perspective, perspective_video_extract_cmd, replay_video_extract_cmd, origin_video_extract_cmd))
                checkpoint = i
       # Output detected replay results
        for i, replay_checkpoint in enumerate(replay_lists):
            replay_start_frame, replay_end_frame, perspective_start_frame, perspective_end_frame, perspective, cmd1, cmd2, cmd3 = replay_checkpoint
            # Hard assignment for specific video ---> Fix this if you change the detected video
            results.append(['03_P11', replay_start_frame, replay_end_frame, perspective, perspective_start_frame, perspective_end_frame])
            # Split replay videos 
            subprocess.call(cmd1, shell=True)
            subprocess.call(cmd2, shell=True)
            subprocess.call(cmd3, shell=True)
    result_output_file_path = os.path.join(args.output_folder_path, 'run_01.csv')
    columns = ['replay_video', 'replay_start', 'replay_end', 'replay_source_video', 'source_start', 'source_end']
    df = pd.DataFrame(data=results, columns=columns)
    df.to_csv(result_output_file_path, index=False, sep=';')


if __name__ == '__main__':
    args = create_argparse()
    if os.path.exists(args.output_folder_path):
        shutil.rmtree(args.output_folder_path)
    os.makedirs(args.output_folder_path)
    delete_empty_files(args.perspective_rank_list_folder)
    detect_replay_and_sync_multistream(args)