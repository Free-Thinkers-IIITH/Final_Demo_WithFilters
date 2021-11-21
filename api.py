import urllib.request
import json
import time
from rank_mapper import get_rank


# ------------------Disable hash randomization------------------
import os
import sys
hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)
# ---------------------------------------------------------------


def fetch_dblp(topic, hit_count=100):
    url = "https://dblp.org/search/publ/api"
    params = {
        "q": topic,
        "h": hit_count,
        "format": "json"
    }
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as url_:
        data = json.loads(url_.read().decode())
        # get relevant data
        paper_list = list()
        # check if key 'hit' exists in data['result']['hits']
        if 'hits' not in data['result']:
            return paper_list
        if 'hit' not in data['result']['hits']:
            return paper_list
        for entry in data['result']['hits']['hit']:
            paper_info = {}
            if 'info' not in entry:
                continue
            if entry['info']['type'] == 'Conference and Workshop Papers':
                paper_info['title'] = entry['info']['title']
                author_lst = list()
                if 'authors' not in entry['info']:
                    continue
                auths = entry['info']['authors']['author']
                if isinstance(auths, dict):
                    author_lst.append(auths['text'])
                else:
                    for a in auths:
                        author_lst.append(a['text'])
                paper_info['authors'] = author_lst
                paper_info['venue'] = entry['info']['venue'].split()[0].lower()
                paper_info['year'] = entry['info']['year']
                paper_info['id'] = hash(
                    paper_info['title'].lower() +
                    paper_info['venue'] +
                    paper_info['year'])
                paper_info['url'] = entry['info']['url']
                paper_info['rank'] = get_rank(paper_info['venue'])
                paper_info['keyword'] = hash(topic)
                paper_list.append(paper_info)
        # write to file
        # open(topic, 'w').write(json.dumps(paper_list))
        return paper_list


def fetch_semantic_scholar(topic,h):
    h = min(h,100)
    url = "http://api.semanticscholar.org/graph/v1/paper/search" 
    params = { 
        "query": topic,
        "limit": h,
        "fields": "title,authors,venue,year,url" 
    }     
    query_string = urllib.parse.urlencode( params ) 
    url = url + "?" + query_string 
    with urllib.request.urlopen(url) as url_:
        data = json.loads(url_.read().decode())
        paper_list = list()
        for entry in data['data']:
            paper_info = {}
            if entry['title'] == '':
                continue
            paper_info['title'] = entry['title']
            author_lst = list()
            if entry['authors'] is None:
                continue
            for a in entry['authors']:
                if 'name' in a:
                    author_lst.append(a['name'])
                # author_lst.append(a['name'])
            if len(author_lst) == 0:
                continue
            paper_info['authors'] = author_lst
            if entry['venue'] == '':
                continue
            paper_info['venue'] = entry['venue']
            if entry['year'] is None or entry['year'] == '':
                continue
            paper_info['year'] = entry['year']
            if entry['url'] is None:
                continue
            paper_info['url'] = entry['url']
            paper_info['id'] = hash(
                    paper_info['title'].lower() +
                    paper_info['venue'] +
                    str(paper_info['year']))
            paper_info['keyword'] = hash(topic)
            rank = get_rank(paper_info['venue'])
            paper_info['rank'] = rank
            paper_list.append(paper_info)
        return paper_list
# build_rank_dict('ranks1.json')
# build_rank_dict('ranks2.json')

# while True:
#     topic = input("Enter topic: ")
#     hit_count = int(input("Enter hit count: "))
#     if topic == "exit" or hit_count == 0:
#         break
#     else:
#         start = time.time()
#         paper_list = fetch_dblp(topic, hit_count)
#         for paper in paper_list:
#             # print(paper)
#             print(json.dumps(paper, indent=4))
#         print(len(paper_list))
#         print("Time taken: ", time.time() - start)
#         # print("-"*100)
