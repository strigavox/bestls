# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import jsonify

import random
import string
import time
from datetime import datetime

import sqlite3

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.

@app.route('/sqlite3_setup')
def sqlite3_setup():
	conn = sqlite3.connect('database.db')
	print("Opened database successfully")
	conn.execute('CREATE TABLE tblShortLinks (randomCode TEXT, toLink TEXT)')

	conn.execute('CREATE TABLE tblClickLogs (victimIP TEXT, randomCode TEXT, DateTime_ TEXT, timeStamp_ TEXT)')
	print("Table created successfully")
	conn.close()
	return 'Task Completed!'

@app.route('/createnewlink')
def new_link():
	return render_template('createlink.html')

def string_Generator(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

@app.route('/addnewlinkrec', methods = ['POST', 'GET'])
def addnewlinkrec():
	if request.method == 'POST':
		print("POST Method!")
		msg = ""
		try:
			longUrl = request.form['longURL']
			print(request.form['longURL'])
			ranCode = string_Generator()
			print(ranCode)
			con = sqlite3.connect("database.db")
			cur = con.cursor()
			cur.execute("INSERT INTO tblShortLinks (randomCode,toLink) VALUES (?,?)",(ranCode,longUrl))
			con.commit()
			print("Record successfully added")
			msg = "Record successfully added"

		except:
			con.rollback()
			ptint("error in insert operation")
			msg = "error in insert operation"

		finally:
			return render_template("newlinkresult.html",msg = msg, ranCode= request.host_url + "Short\\" + ranCode)
			con.close()

@app.route('/listAllUrls')
def listAllUrls():
	con = sqlite3.connect("database.db")
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("select * from tblShortLinks")
	rows = cur.fetchall()
	return render_template("listlinks.html",rows = rows)

@app.route('/Short/<ranCode>')
def ShortLink(ranCode):
	con = sqlite3.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from tblShortLinks where randomCode = '" + ranCode + "'" )
	res = cur.fetchone()
	print(res[1])
	cur.execute("INSERT INTO tblClickLogs (randomCode,victimIP,timeStamp_,DateTime_) VALUES (?,?,?,?)",(ranCode,request.remote_addr,time.time(),datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
	con.commit()

	return redirect(res[1], code=302)
	con.close()

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def home():
	return 'Hello World'

@app.route("/click_logs", methods=["GET"])
def click_logs():
	con = sqlite3.connect("database.db")
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("select * from tblClickLogs")
	rows = cur.fetchall()
	return render_template("click_logs.html",rows = rows)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr, 'timeStamp' : time.time(), 'time' : datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}), 200

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(debug=True)
