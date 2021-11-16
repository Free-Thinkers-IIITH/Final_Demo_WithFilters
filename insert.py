from pymongo import MongoClient
from pprint import pprint
import json
import urllib.request
from rank_mapper import get_rank

def get_papers(keyword):
    '''This function gets data from dblp api for a particular keyword and returns it'''
    url = "https://dblp.org/search/publ/api" 
    params = { 
        "q": keyword, 
        "h": "30", 
        "format": "json" 
    } 
    query_string = urllib.parse.urlencode( params ) 
    url = url + "?" + query_string 
 
    with urllib.request.urlopen(url) as url_:
        data = json.loads(url_.read().decode())
        return data

    # f=open('machine_learning.json') #Instead of json get from dblp api
    # data=json.load(f)
    # f.close()
    # return data

# def get_rank(conferences,name):
#     '''This function returns the rank of a particular conference'''
#     for conf in conferences:
#         if conf['name']==name:
#             return conf['rank']
#     return None

def map_dblp_data(raw_data,keyword):
    '''This function maps data fetched from dblp api to the data model of the db'''
    final_data=[]
    for data in raw_data:
        temp=dict()
        temp['title']=data['info']['title']
        author_lst=list()
        auths=data['info']['authors']['author']
        if type(auths) is dict:
            author_lst.append(auths['text'])
        else:
            for a in auths:
                author_lst.append(a['text'])
        temp['authors']=author_lst
        temp['venue']=data['info']['venue']
        temp['year']=data['info']['year']
        temp['url']=data['info']['url']
        temp['rank']=data['rank']
        keys=list()
        keys.append(keyword)
        temp['keywords']=keys
        final_data.append(temp)
    return final_data
    

def insert_dblp(keyword):
    '''This function inserts the data from dblp api into database'''
    #Connect to db
    # client = MongoClient('mongodb://localhost:27017/paper_db')
    client = MongoClient('mongodb+srv://asxz:asxz@cluster0.4g04r.mongodb.net/ssd?retryWrites=true&w=majority')

    db=client.paper_db
    papers_collec=db['papers']
    #Get conference list
    # conference_list=list(db['conferences'].find())
    #Get papers list from dblp api
    paper_list=get_papers(keyword)
    paper_list=paper_list['result']['hits']['hit']
    final_list=list()

    #Add a rank field to the papers that are of Conference and Workshop Papers type
    for paper in paper_list:
        if 'venue' in paper['info'] and paper['info']['type']=='Conference and Workshop Papers':
            # rank=get_rank(conference_list,paper['info']['venue'])
            rank = get_rank(paper['info']['venue'].split()[0].lower())
            if rank is None:
                paper['rank']='NA'
            else:
                paper['rank']=rank
            final_list.append(paper)

    #Map dblp data to our data model
    final_list=map_dblp_data(final_list,keyword)
    #Inserts papers into db
    for paper in final_list:
        p=papers_collec.find_one({'title':paper['title'] , 'year':paper['year']})
        #If a paper already exits, check if it has the current keyword attached
        if p is not None:
            keys_lst=p['keywords']
            #If the current keyword is not present, update it else ignore the paper
            if keyword not in keys_lst:
                keys_lst.append(keyword)
                print(keys_lst)
                papers_collec.update_one({'_id': p['_id']}, { '$set' : {'keywords':keys_lst}})
        #If paper does not exist in the database, insert it
        else:
            papers_collec.insert_one(paper)

# insert_dblp('computer vision')