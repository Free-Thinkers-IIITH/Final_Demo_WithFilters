from flask import Flask, render_template, request, url_for
from flask_paginate import Pagination, get_page_args
# from fetch import fetch_from_db
from dblp import fetch_dblp
from datetime import datetime
from user_management import User
from insert_paper import insert_paper
from rank_mapper import build_rank_dict
import threading
from flask_mongoengine import MongoEngine
import time

#------------------Disable hash randomization------------------
import os
import sys
hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)
    
#----------------------Flask App----------------------------------

app = Flask(__name__)
app.secret_key = "hi there"
user = User()
posts = []

current_theme = 0
conferences = [{"publisher": "IEEE"}, {"publisher": "IOS Press"}, {
    "publisher": "IEEE Computer Society"}, {"publisher": "Springer"}]

topics = [{"subject": "Machine Learning"}, {
    "subject": "Cyber Security"}, {"subject": "Internet of things"}]

build_rank_dict('ranks1.json', 'Acronym')
build_rank_dict('ranks1.json', 'Standard Name')
build_rank_dict('ranks2.json', 'Acronym')
build_rank_dict('ranks2.json', 'Standard Name')

# -----------------------------------DATABASE-----------------------------------
app.config['MONGODB_SETTINGS'] = {
    'db': 'dblp',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)

# create a new collection for papers


class paper_collection(db.Document):
    pid = db.IntField() #hash value
    title = db.StringField()
    year = db.IntField()
    authors = db.ListField(db.StringField())
    venue = db.StringField()
    rank = db.StringField()
    keywords = db.ListField(db.IntField()) #list of keyword hashes
    url = db.StringField()

# create a keyword to paper id mapping
class keyword_collection(db.Document):
    keyword = db.IntField() #hash value
    papers = db.ListField(db.IntField()) #list of paper id (hash value)

#Run in terminal: db.paper_collection.createIndex({"pid":1}, {background:true})
# db.keyword_collection.createIndex({"keyword":1}, {background:true})


def insert_paper_new_design(key, paper_list):
    """
    key -> string eg machine learning
    paper_list -> list of dict
    dict fields -> id,title,year,authors(list),venue,rank,keyword(hash value)
    """
    # insert the papers into the database
    for paper in paper_list:
        pid = paper['id']
        # if id present in papers collection, update keywords
        temp = paper_collection.objects(pid=pid).first()
        if temp:
            # update keywords
            temp.keywords.append(paper['keyword'])
            temp.save()
        else:
            new_paper = paper_collection()
            new_paper.pid = paper['id']
            new_paper.title = paper['title']
            new_paper.year = int(paper['year'])
            new_paper.authors = paper['authors']
            new_paper.venue = paper['venue']
            new_paper.rank = paper['rank']
            new_paper.keywords.append(paper['keyword'])
            new_paper.url = paper['url']
            new_paper.save()
        # update keyword to paper id mapping
        temp = keyword_collection.objects(keyword=hash(key)).first()
        if temp:
            temp.papers.append(paper['id'])
            temp.save()
        else:
            new_keyword = keyword_collection()
            new_keyword.keyword = hash(key)
            new_keyword.papers.append(paper['id'])
            new_keyword.save()
    print('Insertion Completed!')


def get_papers(key, hits=30):
    temp = keyword_collection.objects(keyword=hash(key)).first()
    if temp:
        start = time.time()
        print(f'fetching {key} papers From DB')
        paper_list = list()
        for pid in temp.papers:
            paper_info = dict()
            temp = paper_collection.objects(pid=pid).first()
            paper_info['title'] = temp.title
            paper_info['year'] = temp.year
            paper_info['authors'] = temp.authors
            paper_info['venue'] = temp.venue
            paper_info['rank'] = temp.rank
            paper_info['url'] = temp.url
            paper_list.append(paper_info)
        end = time.time()
        print(f'Total {len(paper_list)} papers fetched in {end-start} seconds')
    else:
        print(f'fetching {key} papers From API')
        start = time.time()
        paper_list = fetch_dblp(key, hits)
        end = time.time()
        print(f'Total {len(paper_list)} papers fetched in {end-start} seconds')
        print('New thread is inserting to db')
        # create a new thread to insert the papers into the database
        t = threading.Thread(target=insert_paper_new_design, args=(key, paper_list))
        t.start()
    return paper_list

# -----------------------------------DATABASE-----------------------------------

@app.route('/')
def index():
    global current_theme
    global posts
    posts = []
    if current_theme == 0:
        return render_template('index.html', theme=current_theme+1, info="Switch to Dark", datetime=str(datetime.now()))
    else:
        return render_template('index.html', theme=current_theme+1, info="Switch to Light", datetime=str(datetime.now()))


@app.route('/mode')
def mode():
    global current_theme
    global posts
    posts = []
    current_theme = 1 - current_theme
    if current_theme == 0:
        return render_template('index.html', theme=current_theme+1, info="Switch to Dark")
    else:
        return render_template('index.html', theme=current_theme+1, info="Switch to Light")


@app.route('/login')
def login():
    return render_template('login.html', theme=current_theme+1)


@app.route('/login/ans', methods=['POST', 'GET'])
def login_ans():
    user.logout()
    name = request.form['username']
    pwd = request.form['password']
    a = user.login(name, pwd)
    if a == 1:
        return render_template('org_insertion.html', theme=current_theme+1)
    elif a == -1:
        return render_template('org_insertion.html', theme=current_theme+1)
    elif a == -2:
        return render_template('login.html', info="Invalid Username", theme=current_theme+1)
    elif a == -3:
        return render_template('login.html', info="Invalid Password", theme=current_theme+1)
    elif a == -4:
        return render_template('login.html', info="Another user is logged in", theme=current_theme+1)


# @app.route('/register')
# def show_regeistration_page():
#     return render_template('register.html')


@app.route('/register_in', methods=['POST', 'GET'])
def register_user():
    a = user.register(request.form['username'], request.form['password'],
                      request.form['email'], request.form['department'])
    if a == 1:
        return render_template('login.html', theme=current_theme+1)
    elif a == -1:
        return "Username taken"
    elif a == -2:
        return "Email taken"


@app.route('/register')
def register():
    return render_template('registration.html', theme=current_theme+1)


@app.route('/register/ans', methods=['POST', 'GET'])
def register_ans():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    department = request.form['department']
    check = user.register(username, password, email, department)
    if check == -1:
        return render_template('registration.html', info='Username already exists!', theme=current_theme+1)
    elif check == -2:
        return render_template('registration.html', info='Email already exists!', theme=current_theme+1)
    else:
        return render_template('registration.html', info="Registered successfully !!!!", theme=current_theme+1)


def get_posts(posts, offset=0, per_page=5):
    return posts[offset: offset + per_page]


@app.route('/search', methods=['POST', 'GET'])
def search():
    global posts
    # if len(posts) == 0:
    if 'search_query' in request.form and request.form['search_query']:
        query = request.form['search_query']
        # posts = fetch_from_db(query)
        #remove extra while space from query
        query = query.strip()
        posts = get_papers(query,1000)
    # page, per_page, offset = get_page_args()
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page
    total = len(posts)
    pagination_posts = get_posts(posts, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # for post in posts:
    #     print(post)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/1', methods=['POST', 'GET'])
def searchFilter1():
    global posts

    filtered = []
    for post in posts:
        if int(post['year']) >= 2010:
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)

    # return render_template('home.html', posts=filtered, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics)


@app.route('/search/filter/2', methods=['POST', 'GET'])
def searchFilter2():
    global posts

    filtered = []
    for post in posts:
        if int(post['year']) >= 2000 and int(post['year']) < 2010:
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/3', methods=['POST', 'GET'])
def searchFilter3():
    global posts

    filtered = []
    for post in posts:
        if int(post['year']) >= 1990 and int(post['year']) < 2000:
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/A*', methods=['POST', 'GET'])
def searchFilterRank1():
    global posts

    filtered = []
    for post in posts:
        if post['rank'] == 'A*':
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/A', methods=['POST', 'GET'])
def searchFilterRank2():
    global posts

    filtered = []
    for post in posts:
        if post['rank'] == 'A':
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/B', methods=['POST', 'GET'])
def searchFilterRank3():
    global posts

    filtered = []
    for post in posts:
        if post['rank'] == 'B':
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/search/filter/C', methods=['POST', 'GET'])
def searchFilterRank4():
    global posts

    filtered = []
    for post in posts:
        if post['rank'] == 'C':
            filtered.append(post)

    page, per_page, offset = get_page_args()
    total = len(filtered)
    pagination_posts = get_posts(filtered, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    # print(posts)
    return render_template('home.html', posts=pagination_posts, title="Paper Ranker", theme=current_theme+1, conferencesList=conferences, topicList=topics, page=page, per_page=per_page, pagination=pagination,)


@app.route('/org_insertion', methods=['POST', 'GET'])
def org_insertion():
    if(user.check()):
        details = dict()
        details['title'] = request.form['title']
        details['authors'] = request.form['authors'].split(',')
        details['venue'] = request.form['venue']
        details['year'] = request.form['year']
        details['access'] = request.form['access']
        details['url'] = request.form['url']
        details['rank'] = request.form['rank']
        details['keywords'] = request.form['field'].split(',')
        # print(details)
        insert_paper(details)
        return render_template('org_insertion.html', theme=current_theme+1)

    else:
        return render_template('login.html', info='You are not logged in', theme=current_theme+1)


@app.route('/logout')
def log_out():
    user.logout()
    return render_template('login.html', theme=current_theme+1)


if __name__ == "__main__":
    app.run(debug=True)
