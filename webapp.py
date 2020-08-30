#!flask/bin/python
import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, render_template, make_response, send_file
from werkzeug.utils import secure_filename
from helpers import allowed_file, generate_click, generate_beats, convert_file, generate_click_only
import json
import random
import string

UPLOAD_FOLDER = './upload/'
CONVERT_FOLDER = './convert/'
CLICKS_FOLDER = './clicks/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERT_FOLDER'] = CONVERT_FOLDER
app.config['CLICKS_FOLDER'] = CLICKS_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            freq = float(request.form['freq'])
            duration = float(request.form['duration'])
            vol_song = (int(request.form['vol_song']))/100
            vol_click = (int(request.form['vol_click']))/100
            retFile = generate_click(file, filename, freq, duration, vol_song, vol_click, app.config['CONVERT_FOLDER'])
            return redirect(url_for('uploaded_file', filename = retFile))
    return render_template('home.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['CONVERT_FOLDER'],
                            filename)

@app.route('/convert', methods = ['POST'])
def convert():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400
  file = request.files['audioFile']
  if file and allowed_file(file.filename):
    converted, sr, newName = convert_file(file, file.filename, file.filename + "_converted.wav", app.config['CONVERT_FOLDER'])
    response = make_response(send_file(os.path.join(app.config['CONVERT_FOLDER'], newName), attachment_filename = "converted.wav", as_attachment = True))
    return response, 200
  else:
    return render_template('badFileType.html'), 400

@app.route('/generate', methods = ['POST'])
def generate():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400
  file = request.files['audioFile']
  if file and allowed_file(file.filename):
    converted, sr, newName = convert_file(file, file.filename, file.filename + "_converted.wav", app.config['CONVERT_FOLDER'])
    click_freq = 880
    click_duration = 0.5
    vol_adj_song = 1
    vol_adj_click = 1
    retName = generate_click_only(converted, file.filename, file.filename + "_clicks.wav", click_freq, click_duration, app.config['CLICKS_FOLDER'])
    response = make_response(send_file(os.path.join(app.config['CLICKS_FOLDER'], retName), attachment_filename = "clicks.wav", as_attachment = True))
    return response, 200
  else:
    return render_template('badFileType.html'), 400

@app.route('/generateFull', methods = ['POST'])
def generateFull():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400
  file = request.files['audioFile']
  if file and allowed_file(file.filename):
    converted, sr, newName = convert_file(file, file.filename, file.filename + "_converted.wav_", app.config['CONVERT_FOLDER'])
    _, beats = generate_beats(converted, sr)
    ret = {
      "beats": beats.tolist(),
      "sr": sr,
    }
    response = make_response(send_file(os.path.join(app.config['CONVERT_FOLDER'], newName), attachment_filename = "converted.wav", as_attachment = True))
    response.headers['X-Beats'] = ret
    return response, 200
  else:
    return render_template('badFileType.html'), 400


@app.route('/generateTwo', methods = ['POST'])
def generateTwo():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400

  click_freq = request.args.get("click_freq")
  click_dur = request.args.get("click_dur")

  if click_freq is None or click_dur is None:
    return render_template('badFileType.html'), 400

  file = request.files['audioFile']
  if file and allowed_file(file.filename):
    letters = string.ascii_lowercase
    hashName = ''.join(random.choice(letters) for i in range(16))

    converted, sr, newName = convert_file(file, file.filename, hashName + "_converted.wav", app.config['CONVERT_FOLDER'])
    retName = generate_click_only(converted, file.filename, hashName + "_clicks.wav", float(click_freq), float(click_dur), app.config['CLICKS_FOLDER'])

    response = make_response()
    response.headers['X-Urls'] = { "convertedPath": newName, "clickPath": retName}
    return response, 200
  else: 
    return render_template('badFileType.html'), 400

@app.route('/get/<filename>')
def converted_file(filename):
  if '_' in filename:
    ext = filename.rsplit('_', 1)[1].lower()
    if(ext == "converted.wav"):
      return send_from_directory(app.config['CONVERT_FOLDER'], filename)
    elif(ext == "clicks.wav"):
      return send_from_directory(app.config['CLICKS_FOLDER'], filename)

app.run(host = "0.0.0.0")