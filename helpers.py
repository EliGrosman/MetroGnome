import os
from librosa import clicks, load
from librosa.beat import beat_track
from librosa.output import write_wav

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_click(file, filename, click_freq, click_duration, vol_adj_song, vol_adj_click, convert_folder):
  
  x, sr, beats = generate_beats(file)

  x_beats = clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(x), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )

  x = x + vol_adj_song
  x_beats = x_beats + vol_adj_click 

  write_wav(os.path.join(convert_folder, filename), x + x_beats, sr = sr)
  return filename

def generate_beats(file):
  inputAudio, sr = load(file)

  _, beats = beat_track(y = inputAudio, sr = sr)

  return(inputAudio, sr, beats)