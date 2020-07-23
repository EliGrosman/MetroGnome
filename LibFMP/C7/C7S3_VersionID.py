"""
Module: LibFMP.C7.C7S3_VersionID
Author: Tim Zunner, Frank Zalkow, Meinard Mueller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP).
"""
import numpy as np
from numba import jit


@jit(nopython=True)
def compute_accumulated_score_matrix(S):
    """Given the score matrix, compute the accumulated score matrix for common subsequence matching with
    step sizes {(1, 0), (0, 1), (1, 1)}

    Notebook: C7/C7S3_CommonSubsequence.ipynb

    Args:
        C: Score matrix

    Returns:
        D: Accumulated score matrix
    """
    N, M = S.shape
    D = np.zeros((N, M))

    D[0, 0] = max(0, S[0, 0])

    for n in range(1, N):
        D[n, 0] = max(0, D[n-1, 0] + S[n, 0])

    for m in range(1, M):
        D[0, m] = max(0, D[0, m-1] + S[0, m])

    for n in range(1, N):
        for m in range(1, M):
            D[n, m] = max(0, D[n-1, m-1] + S[n, m], D[n-1, m] + S[n, m], D[n, m-1] + S[n, m])

    return D


@jit(nopython=True)
def backtracking(D):
    """Given an accumulated score matrix, compute the score-maximizing path for common subsequence matching with
    step sizes {(1, 0), (0, 1), (1, 1)}

    Notebook: C7/C7S3_CommonSubsequence.ipynb

    Args:
        D: Accumulated score matrix

    Returns
        P: Score-maximizing path (list of index pairs)
    """
    # n, m = np.unravel_index(np.argmax(D), D.shape)  # doesn't work with jit
    n, m = divmod(np.argmax(D), D.shape[1])
    P = [(n, m)]

    while ((n, m) != (0, 0) and (D[n, m] != 0)):
        if n == 0:
            cell = (0, m-1)
        elif m == 0:
            cell = (n-1, 0)
        else:
            val = max(D[n-1, m-1], D[n-1, m], D[n, m-1])
            if val == D[n-1, m-1]:
                cell = (n-1, m-1)
            elif val == D[n-1, m]:
                cell = (n-1, m)
            else:
                cell = (n, m-1)
        P.append(cell)
        n, m = cell
    P.reverse()
    return np.array(P)


@jit(nopython=True)
def get_induced_segments(P):
    """Given a score-maximizing path for common subsequence matching, compute the induces segments

    Notebook: C7/C7S3_CommonSubsequence.ipynb

    Args:
        P: Score-maximizing path (list of index pairs)

    Returns
        seq_x: Induced segment of first sequence
        seq_y: Induced segment of second sequence
    """
    seq_x = np.arange(P[0, 0], P[-1, 0] + 1)
    seq_y = np.arange(P[0, 1], P[-1, 1] + 1)
    return seq_x, seq_y
