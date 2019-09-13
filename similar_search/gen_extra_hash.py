import os
from os import path as osp
from PIL import Image
import imagehash
import pickle
from multiprocessing import Pool

CORPUS_PATH = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/perspective_frames/match_4'
REPLAY_PATH = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/perspective_frames/match_4'

def get_hash(path):
    print("Processing {0}".format(path))
    hash = imagehash.phash(Image.open(path))
    return hash

def gen_corpus_path():
    all_scenes = []
    for round in os.listdir(CORPUS_PATH): 
        round_path = osp.join(CORPUS_PATH, round)
        for player in os.listdir(round_path):
            player_path = osp.join(round_path, player)
            for scene in os.listdir(player_path):
                scene_path = osp.join(player_path, scene)
                all_scenes.append(scene_path)
    return all_scenes

def gen_replay_path():
    all_scenes = []
    for vid in os.listdir(REPLAY_PATH):
        vid_path = osp.join(REPLAY_PATH, vid)
        for scene in os.listdir(vid_path):
            scene_path = osp.join(vid_path, scene)
            all_scenes.append(scene_path)
    return(all_scenes)

if __name__ == "__main__":
    all_scenes = pickle.load(open('lists.obj','rb'))
    extra_scenes = gen_corpus_path()

    all_scenes += extra_scenes
    pickle.dump(all_scenes, open('4matches_lists.obj','wb'))

    p = Pool()
    extra_hashes = p.map(get_hash,extra_scenes)
    hashes = pickle.load(open('hashes.obj','rb'))

    hashes += extra_hashes
    pickle.dump(hashes, open('4matches_hashes.obj','wb'))

