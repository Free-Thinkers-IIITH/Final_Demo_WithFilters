from flask import Flask, render_template, request, url_for
from flask_paginate import Pagination, get_page_args
from fetch import fetch_from_db
from datetime import datetime
from user_management import User
from insert_paper import insert_paper
from rank_mapper import build_rank_dict

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


def get_posts(posts, offset=0, per_page=10):
    return posts[offset: offset + per_page]


@app.route('/search', methods=['POST', 'GET'])
def search():
    global posts
    if len(posts) == 0:
        query = request.form['search_query']
        posts = fetch_from_db(query)
    page, per_page, offset = get_page_args()
    total = len(posts)
    pagination_posts = get_posts(posts, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    for post in posts:
        print(post)
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
