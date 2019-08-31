from pathlib import Path
import sys
import os
import itertools
import argparse
import json
sys.path.append(str(Path(os.getcwd())))
from models.Round import Round


def create_argparse():
    parser = argparse.ArgumentParser(description="Arguments to extract information of matches and rounds")
    parser.add_argument("timelines_folder_path")
    parser.add_argument("output_folder_path")
    return parser.parse_args()


def load_timelines(timelines_folder_path):
    list_files = os.listdir(timelines_folder_path)
    sorted_list_files = sorted(list_files, key=lambda x: int(x.split('.')[0]))
    data = []
    for file in sorted_list_files:
        file_path = os.path.join(timelines_folder_path, file)
        print("Loading file {}".format(file_path))
        content = json.load(open(file_path, 'r'))
        data.append(content)
    data = list(itertools.chain(*data))
    return data


def get_lastest_time(round_info):
    num_rounds = round_info.__len__()
    idx = 1
    filtered_content = []
    while idx < num_rounds:
        if round_info[idx]['type'] == 'round_end' and round_info[idx-1]['type'] == 'round_start':
            filtered_content += round_info[idx-1:idx+1]
            idx += 2
        else:
            idx += 1
    return filtered_content


def extract_round_info(timelines):
    filtered_content = [item for item in timelines if item['type'] == 'round_start' or item['type'] == 'round_end']
    # Filter the list of round again to get the lastest start and end time
    filtered_content = get_lastest_time(filtered_content)
    num_rounds = filtered_content.__len__()
    prev_round_idx = 0
    matches = []
    temp_match_container = []
    for i in range(0, num_rounds, 2):
        round_start = filtered_content[i]
        round_end = filtered_content[i+1]
        round_idx = int(round_start['roundIdx'])
        start_time = round_start['date']
        end_time = round_end['date']
        team_1 = round_start['data']['teams'][0]['id']
        team_2 = round_start['data']['teams'][1]['id']
        ingameTeam_win = round_end['data']['ingameTeam']
        team_id_win = round_end['data']['teamId']
        new_round = Round(round_idx, start_time, end_time, team_1, team_2, ingameTeam_win, team_id_win)
        if prev_round_idx > round_idx:
            matches.append(temp_match_container)
            temp_match_container = [new_round]
        else:
            temp_match_container.append(new_round)
        prev_round_idx = round_idx
    matches.append(temp_match_container)
    return matches


def dump_matches(matches, output_folder_path):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    for i, p in enumerate(matches):
        print("Writing match {} info...".format(i+1))
        match_folder_path = os.path.join(output_folder_path, "match_{}".format(i+1))
        if not os.path.exists(match_folder_path):
            os.makedirs(match_folder_path)
        for round in p:
            print("Writing round {} info...".format(round.round_idx))
            round_file_path = os.path.join(match_folder_path, "round_{}.json".format(str(round.round_idx)))
            json.dump(round.__dict__, open(round_file_path, 'w'), indent=4)


if __name__ == '__main__':
    args = create_argparse()
    timelines = load_timelines(args.timelines_folder_path)
    matches = extract_round_info(timelines)
    dump_matches(matches, args.output_folder_path)