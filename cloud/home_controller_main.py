#!flask/bin/python
import face_recognition
import json
import os
import io
import sys
from flask import Flask, jsonify, make_response, abort, request, redirect, url_for, session, current_app
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug import secure_filename
from os.path import expanduser
from db import *
from hashlib import md5
import numpy as np
import requests
from PIL import Image
from datetime import timedelta
from functools import update_wrapper
from flask_cors import CORS

home = expanduser("~")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/')
def hello_world():
    return 'Hello, World!'


# MULTI USE DELCARATIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auth_user(user):
	cursor = db.cursor()
	cursor.execute('''DELETE FROM currentUser''')
	currentUser.create(user_id = user.id, username_id = user.username)

def get_current_user():
	cursor = db.cursor()
	cursor.execute("SELECT user_id, username_id FROM currentUser")
	result_set = cursor.fetchall()
	for row in result_set:
		return row[0]


def hex_to_img(hex_string):
	byte_array = bytearray.fromhex(hex_string)
	img = Image.frombytes(img.mode, img.size, byte_array)
	img.save('/home/dchau/img.jpg')
	return 'img conversion done'

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



@app.route('/getCurrentMapping', methods=['GET'])
def getCurrentMapping():
    if request.method == 'GET':
        user_id = get_current_user()

        cursor = db.cursor()
        user_map = list()

        cursor.execute("SELECT user_id, gesture, ifttt_descriptor FROM Mappings")
        result_set = cursor.fetchall()
        for row in result_set:
            if (user_id == row[0]):
                user_pair = list()
                user_pair.append(row[1])
                user_pair.append(row[2])
                user_map.append(user_pair)

        return jsonify(user_map)


@app.route('/getCurrentUser', methods=['GET'])
def getCurrentUser():
    if request.method == "GET":
        cursor = db.cursor()
        cursor.execute("SELECT user_id, username_id FROM currentUser")
        result_set = cursor.fetchall()
        for row in result_set:
            return row[1]

@app.route('/logout', methods=['GET'])
def logout():
    cursor = db.cursor()
    cursor.execute('''DELETE FROM currentUser''')
    return 'Success'



# DE1 DECLARATIONS
@app.route('/pictureSegment', methods=['POST'])
def pictureSegement():
	if request.method == 'POST':
		r = request.get_json()

		list_of_pixels = list()
		hex_string = r.get('picture_segment')

		cursor = db.cursor()

		temp = cursor.execute('SELECT max(id) FROM tempPicture')
		max_id = temp.fetchone()[0]

		print(max_id)

		if max_id is None:
			tempPicture.create(picture_segment = hex_string)
			return 'string added'
		elif (int(max_id) < 18):
			tempPicture.create(picture_segment = hex_string)
			return 'string added'
		else:
			cursor.execute('''DELETE FROM tempPicture''')
			tempPicture.create(picture_segment = hex_string)
			print('table reset')
			return 'string added and new table'

	return 'string failed'



@app.route('/joinWithSegments', methods=['GET', 'POST'])
def joinWithSegments():
	if request.method == 'POST':
		r = request.get_json()
		hex_string = ""
		cursor = db.cursor()

		if (r.get('hex_string') == "done"):
			cursor.execute("SELECT id,picture_segment FROM tempPicture")
			result_set = cursor.fetchall()
			for row in result_set:
				hex_string = hex_string + str(row[1])

		cursor.execute('''DELETE FROM tempPicture''')
		print('table reset')

		list_of_pixels = list()

		for i, c in enumerate(hex_string):
			if (i <= len(hex_string) - 6):
				if (i % 6 == 0):
					r_value = int(hex_string[i:i+2], 16)
					g_value = int(hex_string[i+2:i+4], 16)
					b_value = int(hex_string[i+4:i+6], 16)
					rgb_tuple = (r_value,g_value,b_value)
					list_of_pixels.append(rgb_tuple)

		im = Image.new('RGB', (80,60))
		im.putdata(list_of_pixels)
		im.save('/home/dchau/img.png')


		# byte_array = bytearray.fromhex(r.get('hex-string'))
		# img = Image.open(io.BytesIO(byte_array))
		# img.save('/home/dchau/img.jpg')

		picture = face_recognition.load_image_file('/home/dchau/img.png')
		try:
			face_encoding = face_recognition.face_encodings(picture)[0]
		except:
			print('no face appeared')
			return 'User failed to join'

		if (r.get('username') == ""):
			print('no username')
			return 'User failed to join'

		if (r.get('password') == ""):
			print('no password')
			return 'User failed to join'


		try:
			with db.atomic():
				# Attempt to create the user. If the username is taken, due to the
				# unique constraint, the database will raise an IntegrityError.
				user = Users.create(
					username=r.get('username'),
					password=md5((r.get('password')).encode('utf-8')).hexdigest(),
					photo_encoding=face_encoding.tostring(),
					ifttt_requests="")

			# mark the user as being 'authenticated' by setting the session vars
			auth_user(user)
			return 'User joined.'

		except IntegrityError:
			print('That username is already taken')
		return 'User failed to join.'




@app.route('/loginByFaceHexSegments', methods=['GET', 'POST'])    
def loginByFaceHexSegments():
	if request.method == 'POST':
		r = request.get_json()

		hex_string = ""

		if (r.get('hex_string') == "done"):
			cursor = db.cursor()
			cursor.execute("SELECT id,picture_segment FROM tempPicture")
			result_set = cursor.fetchall()
			for row in result_set:
				hex_string = hex_string + str(row[1])

			cursor.execute('''DELETE FROM tempPicture''')
			print('table reset')

		list_of_pixels = list()
		print(len(hex_string))

		for i, c in enumerate(hex_string):
			if (i <= len(hex_string) - 6):
				if (i % 6 == 0):
					r_value = int(hex_string[i:i+2], 16)
					g_value = int(hex_string[i+2:i+4], 16)
					b_value = int(hex_string[i+4:i+6], 16)
					rgb_tuple = (r_value,g_value,b_value)
					list_of_pixels.append(rgb_tuple)

		im = Image.new('RGB', (80,60))
		im.putdata(list_of_pixels)
		im.save('/home/dchau/img.png')

		picture_of_me = face_recognition.load_image_file('/home/dchau/img.png')

		try:
			my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
		except:
			print('no face appeared')
			return 'Fail'

		# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

		cursor = db.cursor()
		cursor.execute("SELECT username, photo_encoding FROM users")
		result_set = cursor.fetchall()
		for row in result_set:
			encoding = np.fromstring(row[1], dtype=my_face_encoding[0].dtype)
			results = face_recognition.compare_faces([my_face_encoding], encoding)
			if results[0] == True:
				user = Users.get(Users.username == row[0])
				auth_user(user)
				print('Success')
				return 'Success'

		print('Fail')
		return 'Fail'




@app.route('/loginByPassword', methods=['GET', 'POST', 'OPTIONS'])    
def loginByPassword():
	if request.method == 'POST' or request.method == 'OPTIONS':

		r = request.get_json()

		username=r.get('username')

		password=md5((r.get('password')).encode('utf-8')).hexdigest()

		# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

		try:
			user = Users.get((Users.username == username) & (Users.password == password))
		except Users.DoesNotExist:
			return 'Fail'
		else:
			auth_user(user)
			return username


		# cursor = db.cursor()
		# cursor.execute("SELECT username, password FROM users")
		# result_set = cursor.fetchall()
		# for row in result_set:
		# 	if (row[0] == username) and (row[1] == password):
		# 		auth_user(user)
		# 		return 'Logged in as ' + str(row[0])

		return 'Fail'




@app.route('/runApplet', methods=['POST'])
def applet():
	if request.method == 'POST':
		r = request.get_json()
		user_id = get_current_user()
		request_name = ""
	    
		cursor = db.cursor();
		cursor.execute("SELECT person_id, ifttt_descriptor, ifttt_requests FROM applets")
		result_set = cursor.fetchall()
		for row in result_set:
			if (user_id == row[0]) and (row[1] == r.get('descriptor')):
				request_name = row[2];

		if (request_name == ""):
			return 'Failure'
			
		requests.post(request_name)
		return 'Success'




@app.route('/changeCurrentMapping', methods=['POST', 'OPTIONS'])
def changeCurrentMapping():
	if request.method == 'POST' or request.method == 'OPTIONS':
		r = request.get_json()

		user_id = get_current_user()

		mapping_list = r.get('mapping')

		cursor = db.cursor()
		cursor.execute('''DELETE FROM Mappings WHERE user_id=?''', (user_id,))

		for i in range(0, len(mapping_list)):
			gesture = mapping_list[i][0]
			action = mapping_list[i][1]
			Mappings.create(user_id = user_id, gesture = gesture, ifttt_descriptor = action)

		return 'Success'





# WEBSITE DECLARATIONS
@app.route('/joinByRGB', methods=['GET', 'POST'])
def joinByRGB():
	if request.method == 'POST':

		width = int(request.form['width'])
		height = int(request.form['height'])

		list_of_pixels = list()
		rgb_string = request.form['picture']
		rgb_list = rgb_string.split(",")

		for i in range(0, len(rgb_list)):
			if (i < len(rgb_list) - 4):
				if (i % 4 == 0):
					r_value = int(rgb_list[i])
					g_value = int(rgb_list[i+1])
					b_value = int(rgb_list[i+2])
					rgb_tuple = (r_value,g_value,b_value)
					list_of_pixels.append(rgb_tuple)


		im = Image.new('RGB', (width,height))
		im.putdata(list_of_pixels)
		im.save('/home/dchau/img.png')


		# byte_array = bytearray.fromhex(r.get('hex-string'))
		# img = Image.open(io.BytesIO(byte_array))
		# img.save('/home/dchau/img.jpg')

		picture = face_recognition.load_image_file('/home/dchau/img.png')
		try:
			face_encoding = face_recognition.face_encodings(picture)[0]
		except:
			print('no face appeared')
			return 'User failed to join'

		if (request.form['username'] == ""):
			print('no username')
			return 'User failed to join'

		if (request.form['password'] == ""):
			print('no password')
			return 'User failed to join'


		try:
			with db.atomic():
				# Attempt to create the user. If the username is taken, due to the
				# unique constraint, the database will raise an IntegrityError.
				user = Users.create(
					username=request.form['username'],
					password=md5((request.form['password']).encode('utf-8')).hexdigest(),
					photo_encoding=face_encoding.tostring(),
					ifttt_requests="")

			# mark the user as being 'authenticated' by setting the session vars
			auth_user(user)
			return request.form['username']

		except IntegrityError:
			print('That username is already taken')
			return 'Username Taken'
		return 'Fail'




@app.route('/loginByRGB', methods=['GET', 'POST'])    
def loginByRGB():
	if request.method == 'POST':
		width = int(request.form['width'])
		height = int(request.form['height'])

		list_of_pixels = list()
		rgb_string = request.form['picture']
		rgb_list = rgb_string.split(",")

		for i in range(0, len(rgb_list)):
			if (i < len(rgb_list) - 4):
				if (i % 4 == 0):
					r_value = int(rgb_list[i])
					g_value = int(rgb_list[i+1])
					b_value = int(rgb_list[i+2])
					rgb_tuple = (r_value,g_value,b_value)
					list_of_pixels.append(rgb_tuple)

		im = Image.new('RGB', (width,height))
		im.putdata(list_of_pixels)
		im.save('/home/dchau/img.png')

		picture_of_me = face_recognition.load_image_file('/home/dchau/img.png')

		try:
			my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
		except:
			print('no face appeared')
			return 'login failed'

		# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

		cursor = db.cursor()
		cursor.execute("SELECT username, photo_encoding FROM users")
		result_set = cursor.fetchall()
		for row in result_set:
			encoding = np.fromstring(row[1], dtype=my_face_encoding[0].dtype)
			results = face_recognition.compare_faces([my_face_encoding], encoding)
			if results[0] == True:
				user = Users.get(Users.username == row[0])
				auth_user(user)
				return str(row[0])

		return 'Fail'



@app.route('/loginByPasswordWebsite', methods=['GET', 'POST', 'OPTIONS'])    
def loginByPasswordWebsite():
	if request.method == 'POST' or request.method == 'OPTIONS':

		username=request.form['username']

		password=md5((request.form['password']).encode('utf-8')).hexdigest()

		# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

		try:
			user = Users.get((Users.username == username) & (Users.password == password))
		except Users.DoesNotExist:
			return 'Fail'
		else:
			auth_user(user)
			return username


		# cursor = db.cursor()
		# cursor.execute("SELECT username, password FROM users")
		# result_set = cursor.fetchall()
		# for row in result_set:
		# 	if (row[0] == username) and (row[1] == password):
		# 		auth_user(user)
		# 		return 'Logged in as ' + str(row[0])

		return 'Fail'





@app.route('/changeCurrentMappingWebsite', methods=['POST', 'OPTIONS'])
def changeCurrentMappingWebsite():
	if request.method == 'POST' or request.method == 'OPTIONS':
		user_id = get_current_user()

		cursor = db.cursor()
		cursor.execute('''DELETE FROM Mappings WHERE user_id=?''', (user_id,))

		mapping_list = request.form['mapping'].split(",")

		for i in range(0, len(mapping_list)):
			if (i <= len(mapping_list) - 2):
				if (i % 2 == 0):
					gesture = mapping_list[i]
					action = mapping_list[i+1]
					Mappings.create(user_id = user_id, gesture = gesture, ifttt_descriptor = action)

		return 'Success'



@app.route('/addApplet', methods=['POST'])
def addApplet():
	if request.method == 'POST':

		user_id = get_current_user()

		cursor = db.cursor()

		cursor.execute("SELECT person_id, ifttt_descriptor FROM applets")
		result_set = cursor.fetchall()
		for row in result_set:
			if (user_id == row[0]) and (request.form['descriptor'] == row[1]):
				return 'Service Exists'

		Applets.create(person_id = user_id, ifttt_descriptor = request.form['descriptor'], ifttt_requests = request.form['url'])

		return 'Success'




@app.route('/deleteApplet', methods=['POST'])
def deleteApplet():
	if request.method == 'POST':

		user_id = get_current_user()
		

		cursor = db.cursor()


		cursor.execute('''DELETE FROM applets WHERE person_id AND ifttt_requests=?''', (user_id, request.form['descriptor']))

		return 'Removed applet'





@app.route('/getUserApplets', methods=['GET'])
def getUserApplets():
	if request.method == 'GET':
		user_id = get_current_user()

		cursor = db.cursor()
		list_of_applets = list()

		cursor.execute("SELECT person_id, ifttt_descriptor FROM applets")
		result_set = cursor.fetchall()
		for row in result_set:
			if (user_id == row[0]):
				list_of_applets.append(row[1])

		print(list_of_applets)

		return jsonify(list_of_applets)



# MISC DECLARATIONS
@app.route('/joinByPicture', methods=['GET', 'POST', 'OPTIONS'])    
# @crossdomain(origin='*')
def joinByPicture():
	if request.method == 'POST' or request.method == 'OPTIONS':
		# check if the post request has the file part
		print(request.form['username'])
		print(request.form['password'])
		if 'file' not in request.files:
			print('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			print('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			picture = face_recognition.load_image_file(file)
			face_encoding = face_recognition.face_encodings(picture)[0]
			print("face encoding done")

			try:
				with db.atomic():
					# Attempt to create the user. If the username is taken, due to the
					# unique constraint, the database will raise an IntegrityError.
					user = Users.create(
						username=request.form['username'],
						password=md5((request.form['password']).encode('utf-8')).hexdigest(),
						photo_encoding=face_encoding.tostring())

				# mark the user as being 'authenticated' by setting the session vars
				auth_user(user)
				return request.form['username']


			except IntegrityError:
				print('That username is already taken')
				return 'Username Taken'
			return 'Fail'


@app.route('/loginByFacePicture', methods=['GET', 'POST'])    
def loginByFacePicture():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			print('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			print('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			picture_of_me = face_recognition.load_image_file(file)

			try:
				my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
			except:
				print('no face appeared')
				return 'login failed'

			# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

			cursor = db.cursor()
			cursor.execute("SELECT username, photo_encoding FROM users")
			result_set = cursor.fetchall()
			for row in result_set:
				encoding = np.fromstring(row[1], dtype=my_face_encoding[0].dtype)
				results = face_recognition.compare_faces([my_face_encoding], encoding)
				if results[0] == True:
					user = Users.get(Users.username == row[0])
					auth_user(user)
					return str(row[0])

			return 'Fail'





if __name__ == '__main__':
	app.secret_key = "reds209ndsldssdsljdsldsdsljdsldksdksdsdfsfsfsfis"
	app.run(host='0.0.0.0', port=6000)
	