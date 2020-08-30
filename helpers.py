import os
from librosa import clicks, load
from librosa.beat import beat_track
import soundfile as sf
from pydub import AudioSegment
from scipy.io import wavfile as wav
import numpy as np

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_click(file, filename, click_freq, click_duration, vol_adj_song, vol_adj_click, convert_folder):
  
  inputAudio, sr, newName = convert_file(file, filename, convert_folder)
  _, beats = generate_beats(inputAudio, sr)
  x = inputAudio
  x_beats = clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(x), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )

  x *= vol_adj_song
  x_beats *= vol_adj_click 

  sf.write(os.path.join(convert_folder, newName), x + x_beats, sr)
  return newName

def generate_click_only(convertedAudio, filename, saveName, click_freq, click_duration, clicks_folder):
  sr = 44100
  _, beats = generate_beats(convertedAudio, sr)
  x = convertedAudio
  x_beats = clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(x), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )
  print(x)
  sf.write(os.path.join(clicks_folder, saveName), x_beats / max(abs(x_beats)), sr)
  return saveName

def generate_beats(inputAudio, sr):

  _, beats = beat_track(y = inputAudio, sr = sr)
  print(inputAudio[:100000])
  return(inputAudio, beats)

def convert_file(file, filename, saveName, convert_folder):
  extension = filename.rsplit('.', 1)[1].lower()
  if(extension == "mp3"):
    audio = AudioSegment.from_mp3(file)
  elif(extension == "wav"):
    audio = AudioSegment.from_wav(file)
  else:
    print("broken")
  audio.export(os.path.join(convert_folder, saveName), format = "wav", bitrate = '16k')
  sr, data = wav.read(os.path.join(convert_folder, saveName))
  # Converts to mono to keep file small
  if len(data.shape) == 2:
    data = data.sum(axis=1) / 2
  data = data / np.max(np.abs(data)) 
  
  return(data, sr, saveName)
