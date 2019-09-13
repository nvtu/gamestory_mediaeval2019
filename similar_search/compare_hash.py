import os
from os import path as osp
import pickle
from multiprocessing import Pool
import json

METADATA = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/replay_detections/metadata'
SEARCH_RESULT = '/home/ninh_tu24111996/MediaEval2019/GameStory/test/new_4matches_hash_search'

def gen_boundaries():
    for i, val in enumerate(corpus):
        path = val.split('/')
        x = int(path[7].split('_')[1])
        y = int(path[8].split('_')[1])
        if  corpus_idx[x][y][0] == -1:
            corpus_idx[x][y][0] = i
        else:
            corpus_idx[x][y][1] = i

def read_metadata():
    for file in os.listdir(METADATA):
        x = open(osp.join(METADATA,file),'r').read().split(',')
        frames_meta[file[:-4]] = [int(x[0]),int(x[1])]

def get_key(item):
    return item[1]
        

def compute_similarity(id,frame_hash):
    print("Processing {0}".format(frames[id]))
    result = []
    frame = frames[id]
    vid_name = frame.split('/')[8]
    [match, round] = frames_meta[vid_name]
    [start, end]  = corpus_idx[match][round]
    for i in range(end-start+1): 
        corpus_id = i+start
        score = (frame_hash - corpus_hash[corpus_id]) / len(frame_hash.hash)**2
        if score < 0.19:
            result.append([corpus[corpus_id], score])
    result = sorted(result, key=get_key) 

    res_path = osp.join(SEARCH_RESULT, vid_name)
    if not osp.exists(res_path):
        os.makedirs(res_path)

    with open(osp.join(res_path, "{0}.csv".format(frame.split('/')[-1][:-4])), 'w') as f:
        for item in result:
            f.write("{0}, {1}\n".format(item[0],item[1]))
    
if __name__ == "__main__":
    print("Loading corpus ...")
    corpus = pickle.load(open('new_4matches_lists.obj','rb'))
    corpus_hash = pickle.load(open('new_4matches_hashes.obj','rb'))


    corpus_idx = [[[-1,-1] for x in range(30)] for y in range(5)]
    gen_boundaries()
    pickle.dump(corpus_idx, open('4matches_lists_idx.obj', 'wb'))
    #corpus_idx = pickle.load(open('lists_idx.obj', 'rb'))

    print("Loading replays ...")
    frames = pickle.load(open('replay_lists.obj','rb'))
    frames_hash = pickle.load(open('replay_hashes.obj','rb'))

    frames_meta = dict()
    read_metadata()

    if not osp.exists(SEARCH_RESULT):
        os.makedirs(SEARCH_RESULT)

    p = Pool()
    p.starmap(compute_similarity, [(x,y) for x,y in enumerate(frames_hash)])



