from pymongo import MongoClient


def insert_paper(details):
    # print("checkkk")
    client = MongoClient(
        'mongodb+srv://asxz:asxz@cluster0.4g04r.mongodb.net/ssd?retryWrites=true&w=majority')
    db = client.paper_db
    papers_collec = db['papers']
    sample_dict = dict()
    sample_dict['title'] = details['title'] if 'title' in details else "NA"
    sample_dict['authors'] = details['authors'] if 'authors' in details else "NA"
    sample_dict['venue'] = details['venue'] if 'venue' in details else "NA"
    sample_dict['year'] = details['year'] if 'year' in details else "NA"
    #sample_dict['access']=details['access'] if 'access' in details else "NA"
    sample_dict['url'] = details['url'] if 'url' in details else "NA"
    sample_dict['rank'] = details['rank'] if 'rank' in details else "NA"
    sample_dict['keywords'] = details['keywords'] if 'keywords' in details else "NA"
    papers_collec.insert_one(sample_dict)


# sample_dict = dict()
# sample_dict['title'] = "xyz"
# sample_dict['authors'] = ["a1", "a2"]
# sample_dict['venue'] = "usa"
# sample_dict['year'] = "2000"
# # sample_dict['access']="xyz"
# sample_dict['url'] = "xyz.abc"
# sample_dict['keywords'] = ["key1", "key2"]

# insert_paper(sample_dict)
