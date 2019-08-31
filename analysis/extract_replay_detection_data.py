import os
import argparse as ap
import subprocess
import shutil
import pandas as pd


default_start_time = 13001 # Match 1 start time in P11 video 03:36:41
extracted_fps = 2
real_fps = 60


def create_argparse():
    parser = ap.ArgumentParser(description="")
    parser.add_argument("video_file_path")
    parser.add_argument("sync_folder_path")
    parser.add_argument("replay_detection_result")
    parser.add_argument("output_folder_path")
    return parser.parse_args()


def get_frame_index(file_path):
    file_name = os.path.basename(file_path)
    frame_index = int(file_name.split('.')[0])
    return frame_index


def to_second(frame_index, fps):
    s = frame_index // fps
    return s


def load_sync_files(sync_folder_path):
    times = []
    infos = []
    files = [os.path.join(sync_folder_path, item) for item in sorted(os.listdir(sync_folder_path))]
    for file_path in files:
        df = pd.read_csv(file_path, delimiter=';')
        for v in df.values:
            match_idx, round_idx, round_start, *r = v
            hour, minute, second = round_start.split(':')
            total_seconds = int(hour) * 3600 + int(minute) * 60 + int(second)
            times.append(total_seconds)
            infos.append((match_idx, round_idx))
    return times, infos



def approximate_replay_detection(args):
    filter_replay_path = os.path.join(args.output_folder_path, 'filter_replay_detection_result')
    if os.path.exists(filter_replay_path):
        shutil.rmtree(filter_replay_path)
    os.makedirs(filter_replay_path)
    threshold = 20 # Replay length should not exceed 20 seconds
    rank_list = [os.path.join(args.replay_detection_result, item) for item in sorted(os.listdir(args.replay_detection_result))]
    num_files = len(rank_list)
    i = 0
    j = 1
    while i < j and i < num_files and j < num_files:
        i_frame_index = get_frame_index(rank_list[i])
        j_frame_index = get_frame_index(rank_list[j])
        i_seconds = to_second(i_frame_index, 2)
        j_seconds = to_second(j_frame_index, 2)
        if j_seconds - i_seconds < threshold:
            output_i_frame_path = rank_list[i].replace(args.replay_detection_result, filter_replay_path)
            cmd = 'cp {} {}'.format(rank_list[i], output_i_frame_path)
            subprocess.call(cmd, shell=True)
            output_j_frame_path = rank_list[j].replace(args.replay_detection_result, filter_replay_path)
            cmd = 'cp {} {}'.format(rank_list[j], output_j_frame_path)
            subprocess.call(cmd, shell=True)
            i += 1
            j += 1
        i += 1
        j += 1


def find_match_and_round(replay_begin_time, times, infos):
    idx = 0
    print(replay_begin_time)
    while idx < times.__len__():
        if replay_begin_time >= times[idx]:
            return infos[idx]
        idx += 1


def extract_replay_data(args):
    video_folder_path = os.path.join(args.output_folder_path, 'replay_videos')
    metadata_folder_path = os.path.join(args.output_folder_path, 'metadata')
    if os.path.exists(video_folder_path):
        shutil.rmtree(video_folder_path)
    if os.path.exists(metadata_folder_path):
        shutil.rmtree(metadata_folder_path)
    os.makedirs(video_folder_path)
    os.makedirs(metadata_folder_path)
    times, infos = load_sync_files(args.sync_folder_path)
    filter_replay_detection_result = os.path.join(args.output_folder_path, 'filter_replay_detection_result')
    results = [os.path.join(filter_replay_detection_result, item) for item in sorted(os.listdir(filter_replay_detection_result))]
    num_replays = results.__len__()
    for i in range(0, num_replays, 2):
        i_frame_index = get_frame_index(results[i])
        j_frame_index = get_frame_index(results[i+1])
        begin_sec = to_second(i_frame_index, extracted_fps) + default_start_time
        end_sec = to_second(j_frame_index, extracted_fps) + default_start_time
        begin_frame = begin_sec * real_fps
        end_frame = end_sec * real_fps
        output_file_path = os.path.join(video_folder_path, '{:07d}_{:07d}.mp4'.format(begin_frame, end_frame))
        delta_time = end_sec - begin_sec
        match_id, round_idx = find_match_and_round(begin_sec, times, infos)
        metadata_output_file_path = output_file_path.replace('.mp4', '.txt')
        metadata_output_file_path = metadata_output_file_path.replace(video_folder_path, metadata_folder_path)
        with open(metadata_output_file_path, 'w') as f:
            print('{},{}'.format(match_id, round_idx), file=f)
        cmd = 'ffmpeg -ss {} -vsync 1 -i {} -strict -2 -t {} -c copy {}'.format(begin_sec, args.video_file_path, delta_time, output_file_path)
        subprocess.call(cmd, shell=True)


def extract_frames_from_replay(args):
    frames_folder_path = os.path.join(args.output_folder_path, 'replay_frames')
    if os.path.exists(frames_folder_path):
        shutil.rmtree(frames_folder_path)
    os.makedirs(frames_folder_path)
    replay_videos_folder_path = os.path.join(args.output_folder_path, 'replay_videos')
    replay_videos = [os.path.join(replay_videos_folder_path, item) for item in sorted(os.listdir(replay_videos_folder_path))]
    for vid in replay_videos:
        vid_name = os.path.basename(vid).split('.')[0]
        vid_frame_folder_path = os.path.join(frames_folder_path, vid_name)
        if not os.path.exists(vid_frame_folder_path):
            os.makedirs(vid_frame_folder_path)
        cmd = 'ffmpeg -i {} -vf fps={} -f image2 {}/%06d.jpg'.format(vid, real_fps, vid_frame_folder_path)
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    args = create_argparse()
    approximate_replay_detection(args)
    extract_replay_data(args)
    extract_frames_from_replay(args)
