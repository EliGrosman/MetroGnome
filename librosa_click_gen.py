import librosa
import os

wav = os.path.join('./audio/dmv.wav')
x, sr = librosa.load(wav)

tempo, beats = librosa.beat.beat_track(y = x, sr = sr)
x_beats = librosa.clicks(frames = beats, sr = sr, length = len(x), click_freq = 1200, click_duration = 0.5)

librosa.output.write_wav("./audio/click.wav", x + x_beats, sr = sr)

