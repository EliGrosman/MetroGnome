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
  
  inputAudio, sr = convert_file(file, filename, convert_folder)
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

  newName = filename.rsplit('.', 1)[0].lower() + ".wav"
  sf.write(os.path.join(convert_folder, newName), x + x_beats, sr)
  return newName

def generate_beats(file, sr):

  _, beats = beat_track(y = inputAudio, sr = sr)

  return(inputAudio, beats)

def convert_file(file, filename, convert_folder):
  extension = filename.rsplit('.', 1)[1].lower()
  if(extension == "mp3"):
    audio = AudioSegment.from_mp3(file)
  elif(extension == "wav"):
    audio = AudioSegment.from_wav(file)
  else:
    print("broken")
  newName = filename + ".wav"
  audio.export(os.path.join(convert_folder, newName), format = "wav", bitrate = '16k')
  sr, data = wav.read(os.path.join(convert_folder, newName))
  # Converts to mono to keep file small
  if len(data.shape) == 2:
    data = data.sum(axis=1) / 2
  # data = data / np.max(np.abs(data)) 
  
  return(data, sr)
