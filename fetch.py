from pymongo import MongoClient
from insert import insert_dblp

def fetch_from_db(keyword):
    # client = MongoClient('mongodb://localhost:27017/paper_db')
    client = MongoClient('mongodb+srv://asxz:asxz@cluster0.4g04r.mongodb.net/ssd?retryWrites=true&w=majority')

    db=client.paper_db
    papers_collec=db['papers'].find({'$text':{'$search':keyword}})# , 'rank':{'$ne':'NA'}})
    paper_lst=list(papers_collec)
    if len(paper_lst) == 0:
        insert_dblp(keyword)
    papers_collec=db['papers'].find({'$text':{'$search':keyword}})# , 'rank':{'$ne':'NA'}})
    paper_lst=list(papers_collec)
    return paper_lst
    # if len(paper_lst) == 0:
    #     #If there is no data with that keyword,
    #     #fetch data from different api's and insert data after preprocessing
    #     #Display the processed data
    #     print("Empty")
    # else:
    #     for doc in paper_lst:
    #         print(doc)

# fetch_from_db("vision machine")