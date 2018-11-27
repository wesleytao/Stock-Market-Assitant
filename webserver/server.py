#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
from flask import Flask
from flask import render_template, jsonify, request, redirect
import requests
import os
from random import choice
from string import ascii_uppercase, digits
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "alm2263"
DB_PASSWORD = "tu8mi5r0"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

user = ''
stock = ''

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)

  if not session.get('logged_in'):
        return render_template('login.html')
  else:
      #
      # example of a database query
      #
      cursor = g.conn.execute(str("SELECT user_id, user_name FROM App_user WHERE user_id = '" + user + "'"))
      ids = []
      names = []
      for result in cursor:
        ids.append(result['user_id'])
        names.append(result['user_name'])
      cursor.close()


      # Flask uses Jinja templates, which is an extension to HTML where you can
      # pass data to a template and dynamically generate HTML based on the data
      # (you can think of it as simple PHP)
      # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
      #
      # You can see an example template in templates/index.html
      #
      # context are the variables that are passed to the template.
      # for example, "data" key in the context variable defined below will be
      # accessible as a variable in index.html:
      #
      #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
      #     <div>{{data}}</div>
      #
      #     # creates a <div> tag for each element in data
      #     # will print:
      #     #
      #     #   <div>grace hopper</div>
      #     #   <div>alan turing</div>
      #     #   <div>ada lovelace</div>
      #     #
      #     {% for n in data %}
      #     <div>{{n}}</div>
      #     {% endfor %}
      #
      context = dict(data = names)


      #
      # render_template looks in the templates/ folder for files.
      # for example, the below file reads template/index.html
      #
      return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/chathome')
def chathome():
  return render_template("chathome.html")


@app.route('/chat', methods=["POST"])
def chat():
    """
    chat end point that performs NLU using rasa.ai
    and constructs response from response.py
    """
    # try:
    response_b = requests.get("http://localhost:5005/conversations/default_sender/respond",
     params={"query": request.form["text"]})
    response = response_b.json()
    if response:
        str = response[0]['text']
        return jsonify({"status": "success", "response": str})
    else:
        print("refresh")
        return redirect("/")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():

  stock = request.form['stock']
  g.conn.execute("INSERT INTO Watchlist VALUES ('" + user + "', '" + stock + "')")
  return redirect('/watchlist')

@app.route('/delete', methods=['POST'])
def delete():
  stock = request.form['stock']
  g.conn.execute("DELETE FROM Watchlist WHERE user_id = '" + user + "' AND ticker = '" + stock + "' IF EXISTS")
  return redirect('/watchlist')



@app.route('/login', methods=['POST'])
def login():
    cursor = g.conn.execute("SELECT user_id FROM App_user")
    names = []
    for result in cursor:
      names.append(result['user_id'])
    cursor.close()

    u = request.form['username']
    p = request.form['password']
    if p == 'password' and u in (names + ["admin"]):
      global user
      user = u
      session['logged_in'] = True
    else:
      flash('Invalid login credentials')
    return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route('/watchlist')
def watchlist():
    cursor = g.conn.execute("SELECT S.name, S.ticker FROM Stock S, Watchlist W WHERE S.ticker = W.ticker AND W.user_id = '" + user + "'")
    stocks = []
    for result in cursor:
        stocks.append((result['name'], result['ticker']))
    cursor.close()

    context = dict(data = stocks)

    return render_template("watchlist.html", **context)

@app.route('/portfolio')
def portfolio():
    cursor = g.conn.execute("SELECT S.name, S.ticker, sum(T.amount) as amount FROM Stock S, Transaction_purchase T WHERE S.ticker = T.ticker AND T.user_id = '" + user + "' GROUP BY S.ticker")
    purchases = []
    for result in cursor:
        name = result['name']
        ticker = result['ticker']
        amount = result['amount']
        cursor2 = g.conn.execute("SELECT close_price FROM Tick WHERE ticker = '" + ticker + "' AND record_date = '2018-10-22'")
        for result2 in cursor2:
            price = result2['close_price']
        cursor2.close()
        purchases.append((name, ticker, amount, price, price*amount))
    cursor.close()

    context = dict(data = purchases)

    return render_template("portfolio.html", **context)

@app.route('/purchase', methods=['POST'])
def purchase():
      stock = request.form['stock']
      amount = request.form['amount']
      ID = ''.join(choice(ascii_uppercase + digits) for _ in range(12))
      g.conn.execute("INSERT INTO Transaction_purchase VALUES ('" + ID + "', '" + user + "', '" + stock + "', '2018-10-22', " + amount + ")");
      return redirect('/portfolio')

@app.route('/stock')
def stockinfo():
    s = request.form['stock']
    if s != '':
        cursor = g.conn.execute("SELECT * FROM Stock WHERE ticker = '" + s + "'")
        for result in cursor:
            context = dict(ticker = result['ticker'], name = result['name'], industry = result['industry'])
            #t = result['ticker']
            #name = result['name']
            #industry = result['industry']
        cursor.close()

        #context = dict(ticker = t, name = name, industry = industry)

    else:
        context = dict(ticker = None, name = None, industry = None)

    return render_template("stock.html", **context)

# =============================================================================
# @app.route('/check')
# def check():
#     global stock
#     stock = request.form['stock']
#     print(stock)
#     return redirect('/stock')
# =============================================================================

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.secret_key = os.urandom(12)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
