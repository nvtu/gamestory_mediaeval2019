import os
from os import path as osp
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from multiprocessing import Pool

es = Elasticsearch()
ses = SignatureES(es, distance_cutoff=0.4)

def add_image_to_corpus(path):
    ses.add_image(path)

paths = pickle.load(open('hashes_path.obj','rb'))
p = Pool()

hashes = p.map(add_image_to_corpus, paths)



