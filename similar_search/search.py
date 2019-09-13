import os
import pickle
import json
from os import path as osp
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from multiprocessing import Pool


es = Elasticsearch()
ses = SignatureES(es, distance_cutoff=0.4)

METADATA = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/replay_detections_logo/metadata'
SEARCH_RESULT = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/4matches_elastic_search_logo_04'
REPLAY_DIR = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/replay_detections_logo/replay_frames'

def read_metadata():
    for file in os.listdir(METADATA):
        x = open(osp.join(METADATA,file),'r').read().split(',')
        frames_meta[file[:-4]] = [int(x[0]),int(x[1])]

def add_image_to_corpus(path):
    ses.add_image(path)

def search_images(path):
    [vid_name, file_name] = path.split('/')[8:10]
    output_path = osp.join(SEARCH_RESULT, vid_name, file_name[:-4]+'.json')
    res = ses.search_image(path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    

def search():
    for vid_name in os.listdir(REPLAY_DIR):
        print("Processing video: {0}".format(vid_name))

        result_path = osp.join(SEARCH_RESULT, vid_name)
        if not osp.exists(result_path):
            os.makedirs(result_path)

        print("---Adding images to engine ...")
        [match,round] = frames_meta[vid_name]
        [start,end] = corpus_idx[match][round]
        p = Pool()
        p.map(add_image_to_corpus,corpus_paths[start:end+1])
        
        print("---Searching replay frames ...") 
        vid_path = osp.join(REPLAY_DIR, vid_name)
        replay_lists = []
        for img in os.listdir(vid_path):
            img_path = osp.join(vid_path, img)
            replay_lists.append(img_path)
        p1 = Pool()
        p1.map(search_images, replay_lists)

        print("---Done!")
        es = Elasticsearch()
        ses = SignatureES(es, distance_cutoff=0.4)

    
if __name__ == "__main__":
    print("Getting paths ...")
    corpus_paths = pickle.load(open('new_4matches_lists.obj','rb'))
    corpus_idx = pickle.load(open('new_4matches_lists_idx.obj', 'rb'))

    frames_meta = dict()
    read_metadata()

    if not osp.exists(SEARCH_RESULT):
        os.makedirs(SEARCH_RESULT)

    search()

