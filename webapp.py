#!flask/bin/python
import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, render_template, make_response, send_file
from werkzeug.utils import secure_filename
from helpers import allowed_file, generate_click, generate_beats, convert_file
import json

UPLOAD_FOLDER = './upload/'
CONVERT_FOLDER = './convert/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERT_FOLDER'] = CONVERT_FOLDER

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

@app.route('/generate', methods = ['POST'])
def generate():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400
  file = request.files['audioFile']
  if file and allowed_file(file.filename):
    converted, sr, newName = convert_file(file, file.filename, app.config['CONVERT_FOLDER'])
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

app.run(host = "0.0.0.0")