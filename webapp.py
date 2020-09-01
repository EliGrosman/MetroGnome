#!flask/bin/python
import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, render_template, make_response, send_file
from werkzeug.utils import secure_filename
from helpers import allowed_file, generate_click
import json
import random
import string

CONVERT_FOLDER = './convert/'
CLICKS_FOLDER = './clicks/'

app = Flask(__name__)
app.config['CONVERT_FOLDER'] = CONVERT_FOLDER
app.config['CLICKS_FOLDER'] = CLICKS_FOLDER



# ---- Endpoints for Web App ----



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            freq = float(request.form['freq'])
            duration = float(request.form['duration'])
            vol_song = (int(request.form['vol_song']))/100
            vol_click = (int(request.form['vol_click']))/100

            retFile = generate_click(file, filename, freq, duration, vol_song, vol_click, app.config['CONVERT_FOLDER'])

            return redirect(url_for('return_file', filename = retFile))
            
    return render_template('home.html')

@app.route('/generated/<filename>')
def return_file(filename):
  return send_from_directory(os.path.join(app.config['CONVERT_FOLDER'], filename))



# ---- Endpoint for Android App ----



@app.route('/generateFull', methods = ['POST'])
def generateFull():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400

  file = request.files['audioFile']

  if file and allowed_file(file.filename):

    click_freq = request.args.get("click_freq")
    click_dur = request.args.get("click_dur")

    if click_freq is None or click_dur is None:
      return render_template('error.html'), 400

    saveName = generate_click(file, file.filename, float(click_freq), float(click_dur), 1, 1, app.config['CONVERT_FOLDER'])

    response = make_response(send_file(os.path.join(app.config['CONVERT_FOLDER'], saveName), attachment_filename = "converted.wav", as_attachment = True))
    
    return response, 200
  
  else:
    return render_template('badFileType.html'), 400



app.run(host = "0.0.0.0")