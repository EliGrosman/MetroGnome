import os
import sys
import numpy as np
from numba import jit
import librosa
from scipy import signal
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import IPython.display as ipd

sys.path.append('..')
import LibFMP.B
import LibFMP.C2
import LibFMP.C6

def compute_PLP(X, Fs, L, N, H, Theta):
    """Compute windowed sinusoid with optimal phase

    Notebook: C6/C6S3_PredominantLocalPulse.ipynb

    Args:
        X: Fourier-based (complex-valued) tempogram
        Fs: Sampling rate
        N: Window length
        H: Hop size
        Theta: Set of tempi (given in BPM)

    Returns:
        nov_PLP: PLP function
    """
    win = np.hanning(N)
    N_left = N // 2
    L_left = N_left
    L_right = N_left
    L_pad = L + L_left + L_right
    nov_PLP = np.zeros(L_pad)
    M = X.shape[1]
    tempogram = np.abs(X)
    for n in range(M):
        k = np.argmax(tempogram[:, n])
        tempo = Theta[k]
        omega = (tempo / 60) / Fs
        c = X[k, n]
        phase = - np.angle(c) / (2 * np.pi)
        t_0 = n * H
        t_1 = t_0 + N
        t_kernel = np.arange(t_0, t_1)
        kernel = win * np.cos(2 * np.pi * (t_kernel * omega - phase))
        nov_PLP[t_kernel] = nov_PLP[t_kernel] + kernel
    nov_PLP = nov_PLP[L_left:L_pad-L_right]
    nov_PLP[nov_PLP < 0] = 0
    return nov_PLP

fn_wav = os.path.join('./audio/dmv.wav')
Fs = 22050
x, Fs = librosa.load(fn_wav, Fs) 

nov, Fs_nov = LibFMP.C6.compute_novelty_spectrum(x, Fs=Fs, N=2048, H=512, gamma=100, M=10, norm=1)
nov, Fs_nov = LibFMP.C6.resample_signal(nov, Fs_in=Fs_nov, Fs_out=100)

L = len(nov)
N = 500
H = 10
Theta = np.arange(30, 601)
X, T_coef, F_coef_BPM = LibFMP.C6.compute_tempogram_Fourier(nov, Fs=Fs_nov, N=N, H=H, Theta=Theta)
nov_PLP = compute_PLP(X, Fs_nov, L, N, H, Theta)

t_nov = np.arange(nov.shape[0]) / Fs_nov

peaks, properties = signal.find_peaks(nov_PLP, prominence=0.5)
peaks_sec = t_nov[peaks]
LibFMP.B.plot_signal(nov_PLP, Fs_nov, color='k', title='PLP function with detected peaks')
plt.plot(peaks_sec, nov_PLP[peaks], 'ro')
plt.show()
x_peaks = librosa.clicks(peaks_sec, sr=Fs, click_freq=1000, length=len(x))
ipd.display(ipd.Audio(x + x_peaks, rate=Fs))
librosa.output.write_wav("./audio/click.wav", x + x_peaks, sr = 22050)
print(x_peaks)