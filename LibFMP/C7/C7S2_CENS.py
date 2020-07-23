"""
Module: LibFMP.C7.C7S2_CENS
Author: Frank Zalkow, Meinard Mueller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP).
"""
import numpy as np
import LibFMP.C3

def quantize_matrix(C, quant_fct=None):
    """Quantize matrix values in a logarithmic manner (as done for CENS features)

    Notebook: C7/C7S2_CENS.ipynb

    Args:
        C: Input matrix
        quant_fct: List specifying the quantization function

    Returns:
        C_quant: Output matrix
    """
    C_quant= np.empty_like(C)
    if quant_fct is None:
        quant_fct = [(0.0, 0.05, 0), (0.05, 0.1, 1), (0.1, 0.2, 2),
                     (0.2, 0.4, 3), (0.4, 1, 4)]
    for min_val, max_val, target_val in quant_fct:
        mask = np.logical_and(min_val <= C, C < max_val)
        C_quant[mask] = target_val
    return C_quant


def compute_CENS_from_chromagram(C, Fs=1, ell=41, d=10, quant=True):
    """Compute CENS features from chromagram

    Notebook: C7/C7S2_CENS.ipynb

    Args:
        C: Input chromagram
        Fs: Feature rate of chromagram
        ell: Smoothing length
        d: Downsampling factor
        quant: Apply quantization

    Returns:
        C_cens: CENS features
        F_cens: Feature rate of CENS features
    """
    C_norm = LibFMP.C3.normalize_feature_sequence(C, norm='1')
    if quant:
        C_Q = quantize_matrix(C_norm)
    else:
        C_Q = C_norm
    C_smooth, Fs_cens = LibFMP.C3.smooth_downsample_feature_sequence(C_Q, Fs,
                                    filt_len=ell, down_sampling=d, w_type='hann')
    C_cens = LibFMP.C3.normalize_feature_sequence(C_smooth, norm='2')

    return C_cens, Fs_cens
