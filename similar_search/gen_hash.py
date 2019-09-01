import os
from os import path as osp
from PIL import Image
import imagehash
import pickle
from multiprocessing import Pool

CORPUS_PATH = '/home/tu_ninhvan/www2.itec.aau.at/mediaeval19/test/perspective_frames'

def get_hash(path):
    print("Processing {0}".format(path))
    hash = imagehash.phash(Image.open(path))
    return hash

all_scenes = []
for match in os.listdir(CORPUS_PATH): 
    match_path = osp.join(CORPUS_PATH,match)
    for round in os.listdir(match_path): 
        round_path = osp.join(match_path, round)
        print("Processing {0} - {1}".format(match, round))
        for player in os.listdir(round_path):
            player_path = osp.join(round_path, player)
            for scene in os.listdir(player_path):
                scene_path = osp.join(player_path, scene)
                all_scenes.append(scene_path)
pickle.dump(all_scenes, open('lists.obj','wb'))

p = Pool()
hashes = p.map(get_hash,all_scenes)
pickle.dump(hashes, open('hashes.obj','wb'))

