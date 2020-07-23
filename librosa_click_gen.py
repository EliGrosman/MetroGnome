import librosa
import os

wav = os.path.join('./audio/dmv.wav')

# Calculate an array of amplitudes (x) the sample rate (sr) for the input file
x, sr = librosa.load(wav)

# Calculate tempo and array of beats from input file
tempo, beats = librosa.beat.beat_track(y = x, sr = sr)

# Generate the clicktrack
x_beats = librosa.clicks(
            frames = beats,      # the beats to place clicks
            sr = sr,             # sample rate
            length = len(x),     # length of the song (necessary to align clicktrack and song)
            click_freq = 1200,   # frequency of each click (in Hz)
            click_duration = 0.5 # duration of each click (in seconds)
          )

# Adjust the volume. vol_adj is in decibles
vol_adj_click = -0.5
vol_adj_song = 0

x = x + vol_adj_song
x_beats = x_beats + vol_adj_click 

# Export
librosa.output.write_wav("./audio/click.wav", x + x_beats, sr = sr)

