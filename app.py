from flask import Flask, render_template, request, jsonify, redirect, url_for, session, escape
from flask.ext.pymongo import PyMongo
from random import randint


app = Flask(__name__)

import private
import random

app.config['MONGO_URI'] = private.DATABASEURL
mongo = PyMongo(app)


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/add_quote')
def add():
    if 'username' in session:
        return render_template('add.html')

    return 'Please login'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return 'Home, not homepage'


#Add Quote functionality

@app.route('/add_quote', methods=['POST'])
def submit_quote():
    if request.method == 'POST':
        quote = request.form['quote']
        quote_by = request.form['quote-by']

        get_username = escape(session['username'])
        get_user = mongo.db.users.find_one({'Username': get_username})
        api_key = get_user['Key']

        quote_filter(quote)
        tweetable = quote_filter.tweetable

        quote_collection = mongo.db.users_quotes
        quote_collection.insert({'Quote': quote, 'Tweetable': tweetable, 'By': quote_by, 'Username': get_username, 'Key': api_key})

        return redirect(url_for('home'))
    return 'Error'

@app.route('/api/random', methods=['GET'])
def random_quote():
    collection = mongo.db.quotes
    quotes = []

    for doc in collection.find():
        quotes.append([doc['Quote'],doc['By'],doc['Tweetable']])

    quote_list = random.choice(quotes)
    quote_dic = {"Quote": quote_list[0], "By": quote_list[1], "Tweetable": quote_list[2]}

    return jsonify(quote_dic)

@app.route('/api/quotes/secret_key=<path:api_key>', methods=['GET'])
def get_user_quotes(api_key):
    if request.method == 'GET':
        collection = mongo.db.users_quotes

        get_key = request.path[23:]
        quotes = []

        for doc in collection.find():
            quotes.append([doc['Quote'], doc['By'], doc['Tweetable']])
        quote_list = random.choice(quotes)
        quote_dic = {"Quote": quote_list[0], "By": quote_list[1], "Tweetable": quote_list[2]}
        return jsonify(quote_dic)

#Authentication

@app.route('/signup', methods=['POST'])
def signup_user():
    if request.method == 'POST':
        get_username = request.form['username']
        get_password = request.form['password']

        #User API KEY
        key = api_key()

        users = mongo.db.users
        

        users.insert({'Username': get_username, 'Password': get_password, 'Key': key})
        return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        get_username = request.form['username']
        get_password = request.form['password']

        get_user = mongo.db.users.find_one({'Username': get_username})

        main_password = get_user['Password']

        if get_password != main_password:
            return 'Unvalid Password'
        else:
            session['username'] = get_username
            return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

def quote_filter(q):
    q_len = len(q)

    if q_len > 140:
        quote_filter.tweetable = False
    else:
        quote_filter.tweetable = True;


def api_key():
    a = 0
    start_int = randint(0,75)
    key = start_int
    str(key)
    for i in range(7):

        if a % 2 == 0 and a != 0:
            a = a + 1
            random_int = randint(0,257)
            key = str(key) + str(random_int)

        elif a == 0:
            a = a + 1
            random_int = randint(300,567)
            key = str(key) + str(random_int)
        else:
            a = a + 1
            random_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            key = str(key) + str(random_char)
    return key

app.secret_key = private.SECRETKEY

if __name__ == "__main__":
    app.run()

