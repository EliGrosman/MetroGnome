import os
from librosa import clicks, load
from librosa.beat import beat_track
import soundfile as sf
from pydub import AudioSegment
from scipy.io import wavfile as wav

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_click(file, filename, click_freq, click_duration, vol_adj_song, vol_adj_click, convert_folder):
  
  inputAudio = convert_file(file)
  x, sr, beats = generate_beats(inputAudio, 0)

  x_beats = clicks(
            frames = beats, # the beats to place clicks
            sr = sr, # sample rate
            length = len(x), # length of the song (necessary to align clicktrack and song)
            click_freq = click_freq, # frequency of each click (in Hz)
            click_duration = click_duration # duration of each click (in seconds)
          )

  x = x + vol_adj_song
  x_beats = x_beats + vol_adj_click 

  sf.write(os.path.join(convert_folder, filename), x + x_beats, sr)
  return filename

def generate_beats(file, sr):

  # Converted files are saved to /upload/ so we load them from their path
  if(isinstance(file, str)):
    inputAudio, sr = load("./upload/" + file)
  else:
    inputAudio = file

  _, beats = beat_track(y = inputAudio, sr = sr)

  return(inputAudio, sr, beats)

def convert_mp3(file, filename, upload_folder):
  audio = AudioSegment.from_mp3(file)
  newName = filename + ".wav"
  audio.export(os.path.join(upload_folder, newName), format="wav")
  return(newName)


def convert_file(file, filename, convert_folder):
  extension = filename.rsplit('.', 1)[1].lower()
  if(extension == "mp3"):
    audio = AudioSegment.from_mp3(file)
  else if(extension == "wav"):
    audio = AudioSegment.from_wav(file)
  else:
    print("broken")
  newName = filename + ".wav"
  audio.export(os.path.join(convert_folder, newName), format = "wav", bitrate = '16k')
  sr, data = wav.read(os.path.join(convert_folder, newName))
  if len(data.shape) == 2:
    data = data.sum(axis=1) / 2
  return data, sr
