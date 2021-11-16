from flask import session
from pymongo import MongoClient
import bcrypt
import pymongo


class User:
    def __init__(self):
        client = MongoClient(
            'mongodb+srv://asxz:asxz@cluster0.4g04r.mongodb.net/ssd?retryWrites=true&w=majority')
        db = client.paper_db
        #client = pymongo.MongoClient("mongodb://localhost:27017/")
        #db = client.get_database('ssd')
        self.records = db.login_credentials

    def register(self, username, password, email, department):
        user_found = self.records.find_one({"username": username})
        email_found = self.records.find_one({"email": email})
        if user_found:
            # return 'Username already exixsts!'
            return -1
        if email_found:
            # return 'Email already exists!'
            return -2
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_input = {'username': username, 'email': email,
                      'password': hashed, 'department': department}
        self.records.insert_one(user_input)
        # return "registration successfull"
        return 1

    def check(self):
        if "username" in session:
            return True
        else:
            return False

    def login(self, username, password):
        if self.check():
            if session['username'] == username:
            # return ' user logged in'
                return -1
            else:
            # return ' another user logged in'
                return -4
        user_found = self.records.find_one({"username": username})
        if not user_found:
            # return 'No Such username'
            return -2
        if bcrypt.checkpw(password.encode('utf-8'), user_found['password']):
            self.username = username
            self.email = user_found['email']
            self.department = user_found['department']
            session["username"] = username
            # return "successfully logged in"
            return 1
        else:
            # return "incorrect password"
            return -3

    def logout(self):
        self.username = ""
        self.email = ""
        self.department = ""
        session.pop("username", None)
