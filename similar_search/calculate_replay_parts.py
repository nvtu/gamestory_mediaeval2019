import os
import pickle
import json
from os import path as osp
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from multiprocessing import Pool
from PIL import Image
import imagehash
from pprint import pprint

METADATA = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/replay_detections/metadata'
SEARCH_RESULT = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/4matches_elastic_search_06'
REPLAY_DIR = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/replay_detections/replay_frames'


vid_path = osp.join(REPLAY_DIR, '0833340_0833820')

img_list = []
for img in os.listdir(vid_path):
    img_path = osp.join(vid_path, img)
    img_list.append(img_path)

img_list = sorted(img_list)

last = imagehash.phash(Image.open(img_list[0]))
for i in range(img_list.__len__()-1):
    cur_hash = imagehash.phash(Image.open(img_list[i+1]))
    print(img_list[i+1].split('/')[-1], cur_hash-last)
    last = cur_hash

