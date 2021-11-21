from models import *
import threading
import json
import time
def build_rank(file_name):
    with open(file_name) as f:
        for conf in json.load(f):
            rank = conf['Rank']
            conf_id = hash(conf['Standard Name'].lower())
            if not Conference.objects(conf_id=conf_id,).first():
                Conference(conf_id=conf_id, rank=rank).save()
            conf_id = hash(conf['Acronym'].lower())
            if not Conference.objects(conf_id=conf_id).first():
                Conference(conf_id=conf_id, rank=rank).save()
def get_rank(conf_name):
    conf_name = conf_name.lower()
    conf_id = hash(conf_name.split()[0])
    temp = Conference.objects(conf_id=conf_id).first()
    if temp:
        return temp.rank
    else:
        conf_id = hash(conf_name)
        temp = Conference.objects(conf_id=conf_id).first()
        if temp:
            return temp.rank
    return None

#if paper_collection is empty, run this function
def insert_conf_ranks():
    files = ['Ranks/rank1.json','Ranks/rank2.json','Ranks/rank3.json']
    print('Inserting Conference Ranks')
    start = time.time()
    threads = []
    for file_name in files:
        threads.append(threading.Thread(target=build_rank, args=(file_name,)))
        threads[-1].start()
    for thread in threads:
        thread.join()
    print('Conference Rank Insertion Completed!')
    print(f'Total Time Taken: {time.time()-start} seconds')


# import json
# conf_rank = dict()

# def build_rank_dict(file_name,field_name):
#     with open(file_name) as f:
#         for conf in json.load(f):
#             conf_rank[conf[field_name].lower()] = conf['Rank']
# def get_rank(conf_name):
#     if conf_name in conf_rank:
#         return conf_rank[conf_name]
#     else:
#         return None

# build_rank_dict('ranks1.json','Acronym')
# build_rank_dict('ranks1.json','Standard Name')
# build_rank_dict('ranks2.json','Acronym')
# build_rank_dict('ranks2.json','Standard Name')

# for conf in conf_rank:
#     print(conf, conf_rank[conf])
