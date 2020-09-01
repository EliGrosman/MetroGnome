import os
from librosa import clicks
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
  saveFileExt = filename.rsplit('.', 1)[1].lower()
  saveName = filename

  if(saveFileExt != "wav"):
    saveName = saveName.rsplit('.', 1)[0].lower() + ".wav"

  inputAudio, _, newName = convert_file(file, filename, saveName, convert_folder)
  sr = 44100

  _, beats = beat_track(inputAudio, sr)

  clickAudio = clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(inputAudio), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )

  inputAudio *= vol_adj_song
  clickAudio *= vol_adj_click 

  sf.write(os.path.join(convert_folder, newName), inputAudio + clickAudio, sr)
  return newName

def convert_file(file, filename, saveName, convert_folder):
  extension = filename.rsplit('.', 1)[1].lower()

  if(extension == "mp3"):
    audio = AudioSegment.from_mp3(file)
  elif(extension == "wav"):
    audio = AudioSegment.from_wav(file)
  else:
    audio = AudioSegment.from_file(file, extension)

  audio.export(os.path.join(convert_folder, saveName), format = "wav", bitrate = '16k')

  sr, data = wav.read(os.path.join(convert_folder, saveName))

  # Converts to mono to keep file small and usable with beat_track
  if len(data.shape) == 2:
    data = data.sum(axis=1) / 2

  # Normalize amplitudes
  data = data / np.max(np.abs(data)) 
  
  return(data, sr, saveName)
