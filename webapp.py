#!flask/Scripts/python
import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import librosa
from librosa.beat import beat_track

UPLOAD_FOLDER = './upload/'
CONVERT_FOLDER = './convert/'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERT_FOLDER'] = CONVERT_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_click(filename, click_freq, click_duration, vol_adj_song, vol_adj_click):
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
  x, sr = librosa.load(file_path)

  tempo, beats = beat_track(y = x, sr = sr)

  x_beats = librosa.clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(x), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )

  x = x + vol_adj_song
  x_beats = x_beats + vol_adj_click 

  librosa.output.write_wav(os.path.join(app.config['CONVERT_FOLDER'], filename), x + x_beats, sr = sr)
  return send_from_directory(app.config['CONVERT_FOLDER'],
                               filename)
  
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            freq = float(request.form['freq'])
            duration = float(request.form['duration'])
            vol_song = (int(request.form['vol_song'])-50)/10
            vol_click = (int(request.form['vol_click'])-50)/10
            generate_click(filename, freq, duration, vol_song, vol_click)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Generate Clicktrack</title>
    <h1>Generate Clicktrack</h1>
    <form method=post enctype=multipart/form-data>
      <label for=file>Upload file (Accepts .wav, .mp3)</label><br>
      <input type=file id=file name="file"><br>
      <label for=freq>Click frequency (in db)</label><br>
      <input type=number id=freq name=freq placeholder="880"><br>
      <label for=duration>Click duration (in seconds)</label><br>
      <input type=number id=duration name=duration placeholder="0.50" step ="0.01" min=0 max=5><br>
      <label for=vol_song>Song volume</label><br>
      <input type=range id=vol_song name=vol_song><br>
      <label for=vol_click>Click volume</label><br>
      <input type=range id=vol_click name="vol_click"><br>
      <input type=submit value=Upload>
    </form>
    <br>
    <h3>Demos</h3>
    <a href="/uploads/dmv.wav">DMV - Primus</a><br>
    <a href="/uploads/another_one_bites_the_dust.wav">Another One Bites the Dust - Queen</a><br>
    <a href="/uploads/ANTEMASQUE_4AM.mp3">4AM - ANTEMASQUE (detected beats on 2 and 4)</a>
    '''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['CONVERT_FOLDER'],
                            filename)

app.run(host = "0.0.0.0")