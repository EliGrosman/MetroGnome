"""
Module: LibFMP.B.B_Sonification
Author: Meinard Mueller, Tim Zunner, Angel Villar-Corrales
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP).
"""

import numpy as np
import pandas as pd
import librosa, os, math, csv
from scipy import signal
from matplotlib import pyplot as plt
PI = math.pi

# Requires files "data/B/plato.wav" and so on, which are not part of LibFMP -> generates error
#sonficiations
plato = librosa.load(".."+"/data/B/plato.wav")[0]
electro = librosa.load(".."+"/data/B/electro.wav")[0]
beat = librosa.load(".."+"/data/B/beat.wav")[0]
c_chord = librosa.load(".."+"/data/B/c.wav")[0]
d_chord = librosa.load(".."+"/data/B/d.wav")[0]
e_chord = librosa.load(".."+"/data/B/e.wav")[0]


##########################################
# Method that returns an audio segment for the given label
#########################################
def get_sound(label, chord=True):

    #sound effects
    if(chord==False):
        if(label==1):
            sound = plato
        elif(label==2):
            sound = beat
        elif(label==3):
            sound = electro
        else:
            sound = plato

    #chords
    else:
        if(label==1):
            sound = c_chord
        elif(label==2):
            sound = d_chord
        elif(label==3):
            sound = e_chord
        else:
            sound = c_chord

    N = len(sound)
    return sound, N


##########################################
# Method that returns a sinusoid for the givel label
#########################################
def get_sinusoid(label, Fs):

    if(label==1):
        num_periods = 8
        f_sine = 800
    elif(label==2):
        num_periods = 16
        f_sine = 1600
    elif(label==3):
        num_periods = 32
        f_sine = 3200
    else:
        num_periods = 8
        f_sine = 880

    sound = np.sin(np.linspace(0, num_periods * 2 * np.pi, num_periods*Fs//f_sine))
    N = len(sound)

    return sound, N



##########################################
# Method that returns a frequency for the givel label
#########################################
def get_frequency(label):

    if(label==1):
        freq = 1000
    elif(label==2):
        freq = 2000
    elif(label==3):
        freq = 4000
    else:
        freq = 1000

    return freq





##########################################
# Method that computes the own sonification
#########################################
def sonification_own( peaks, amplitudes, labels, length, Fs=44100, method="chords", scaling=True, mode="left" ):

    sonification = np.zeros( length )

    for i in range(len(labels)):

        #obtaining the corresponding audio segment
        if(method=="chords"):
            sound, N = get_sound(labels[i], True)
        else:
            sound, N = get_sound(labels[i], False)

        #scaling the segment
        sound = sound/np.max(sound)
        if(scaling==True):
            sound *= amplitudes[i]

        #updating the sonification using the given mode
        if(mode=="left"):
            start = int(peaks[i]*Fs)
            end = start + N
        elif(mode=="right"):
            start = int(peaks[i]*Fs) - N
            end = start + N
        else:
            start = int(peaks[i]*Fs)-int(N/2)
            end = start + N

        #taking care of the boundaries
        if(start<0):
            start = 0
            sound = sound[-end:]
        if(end>len(sonification)):
            end = len(sonification)
            sound = sound[:end-start]

        sonification[start:end] = sound


    return sonification



##########################################
# Method that computes Librosa sonification
#########################################
def sonification_librosa( peaks, amplitudes, labels, length, Fs=44100, scaling=True ):

    #applying librosa sonification
    sonification = np.zeros( length )

    #computing the sonifications for every label
    for i in [1,2,3]:

        idxs = np.where(labels==i)
        current_peaks = peaks[idxs]
        freq = get_frequency(i)

        current_sonification = librosa.clicks(current_peaks, sr=Fs, click_freq=freq, length=length)
        sonification += current_sonification

    #scaling the sonificiations with the amplitude of the novelty curvve
    if(scaling==True):
        for i in range(len(peaks)):
            current_peak = int(peaks[i]*Fs)
            length = int(0.1*Fs)
            window = np.ones(length) #length of sonification is 100ms
            window = window*amplitudes[i]
            sonification[current_peak:current_peak+length] *= window

    return sonification



##########################################
# Method that computes the sonification from HPSS lab
#########################################
def sonification_hpss_lab(novelty, length, Fs, Fs_nov):

    pos = np.append(novelty, novelty[-1]) > np.insert(novelty, 0, novelty[0])
    neg = np.logical_not(pos)
    peaks = np.where(np.logical_and(pos[:-1], neg[1:]))[0]

    values = novelty[peaks]
    values /= np.max(values)
    peaks = peaks[values >= 0.01]
    values = values[values >= 0.01]
    peaks_idx = np.int32(np.round(peaks / Fs_nov * Fs))

    sine_periods = 8
    sine_freq = 880
    click = np.sin(np.linspace(0, sine_periods * 2 * np.pi, sine_periods * Fs//sine_freq))
    ramp = np.linspace(1, 1/len(click), len(click)) ** 2
    click = click * ramp

    out = np.zeros(length)
    for i, start in enumerate(peaks_idx):
        idx = np.arange(start, start+len(click))
        out[idx] += (click * values[i])

    return out, peaks






##########################################
def save_to_csv( path, file_name, time, amplitudes, labels ):

    #creating pandas df
    data = list(zip(time, amplitudes, labels))
    df = pd.DataFrame(data, columns = ['Time (sec)', 'Amplitude', "Label"])

    #exporting the df to a csv file
    df.to_csv( path + "/"+ file_name )

    return



##########################################
def load_from_csv( path, file_name):

    df = pd.read_csv( path + "/" + file_name )
    time = df.loc[:,"Time (sec)"].values
    amplitudes = df.loc[:,"Amplitude"].values
    labels = df.loc[:,"Label"].values

    return {
        "time":time,
        "amplitudes":amplitudes,
        "labels":labels
    }
