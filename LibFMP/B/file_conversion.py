import numpy as np
import pandas as pd
import librosa
import os
import sys
sys.path.append(os.path.join('..'))
import LibFMP.B.audio as aud


def save_normalized_seg(in_path, out_path, start_time, end_time, Fs=22050):
    x, Fs = librosa.load(in_path, sr=Fs, offset=start_time, duration=end_time-start_time)
    x_norm = x / np.max(np.abs(x))
    
    aud.write_audio(out_path+'.wav', x_norm, Fs)
    #aud.write_audio(out_path+'.mp3', x_norm, Fs)


def format_csv_file(in_path, out_path, start_time, end_time):
    df = pd.read_csv(in_path, sep=',')
    
    data_array = []
    for i, (start, end, pitch, label) in df.iterrows():
        if (start > start_time) and (start < end_time):
            data_array.append([start-start_time, min(end, end_time)-start, int(pitch), 0, str(int(label))])
    
    #data_array = np.array(data_array)
    columns = ["Start", "Duration", "Pitch", "Velocity", "Instrument"]
    df_out = pd.DataFrame(data_array, columns=columns)
    df_out.to_csv(out_path, sep=';', index=False)


example_name = 'Schubert_D911-02_HU33'
start_sec = 8.5
end_sec = 17.17
Fs = 22050

audio_path = os.path.join('..', 'data', example_name + '_audio.wav')
audio_path_out = os.path.join('..', 'data', 'FMP_B_' + example_name + '_seg')

csv_path = os.path.join('..', 'data', example_name + '_pitch.csv')
csv_path_out = os.path.join('..', 'data', 'FMP_B_' + example_name + '_seg_pitch.csv')

save_normalized_seg(audio_path, audio_path_out, start_sec, end_sec, Fs=Fs)

format_csv_file(csv_path, csv_path_out, start_sec, end_sec)

