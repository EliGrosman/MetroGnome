"""
Module: LibFMP.C7.C7S2_SDTW
Author: Frank Zalkow, Meinard Mueller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP).
"""
from numba import jit
import numpy as np


@jit(nopython=True)
def compute_accumulated_cost_matrix(C):
    """Given the cost matrix, compute the accumulated cost matrix for subsequence dynamic time warping with
    step sizes {(1, 0), (0, 1), (1, 1)}

    Notebook: C7/C7S2_SubsequenceDTW.ipynb

    Args:
        C: cost matrix

    Returns:
        D: Accumulated cost matrix
    """
    N, M = C.shape
    D = np.zeros((N, M))
    D[:, 0] = np.cumsum(C[:, 0])
    D[0, :] = C[0, :]
    for n in range(1, N):
        for m in range(1, M):
            D[n, m] = C[n, m] + min(D[n-1, m], D[n, m-1], D[n-1, m-1])
    return D


@jit(nopython=True)
def compute_optimal_warping_path(D):
    """Given an accumulated cost matrix, compute the warping path for subsequence dynamic time warping with
    step sizes {(1, 0), (0, 1), (1, 1)}

    Notebook: C7/C7S2_SubsequenceDTW.ipynb

    Args:
        D: Accumulated cost matrix

    Returns
        P: Warping path (list of index pairs)
    """
    N, M = D.shape
    n = N - 1
    m = D[N - 1, :].argmin()
    P = [(n, m)]

    while n > 0:
        if m == 0:
            cell = (n - 1, 0)
        else:
            val = min(D[n-1, m-1], D[n-1, m], D[n, m-1])
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
def compute_accumulated_cost_matrix_21(C):
    """Given the cost matrix, compute the accumulated cost matrix for subsequence dynamic time warping with
    step sizes {(1, 1), (2, 1), (1, 2)}

    Notebook: C7/C7S2_SubsequenceDTW.ipynb

    Args:
        C: cost matrix

    Returns:
        D: Accumulated cost matrix
    """
    N, M = C.shape
    D = np.zeros((N + 1, M + 2))
    D[0:1, :] = np.inf
    D[:, 0:2] = np.inf

    D[1, 2:] = C[0, :]

    for n in range(1, N):
        for m in range(0, M):
            if n == 0 and m == 0:
                continue
            D[n+1, m+2] = C[n, m] + min(D[n-1+1, m-1+2], D[n-2+1, m-1+2], D[n-1+1, m-2+2])
    return D


@jit(nopython=True)
def compute_optimal_warping_path_21(D):
    """Given an accumulated cost matrix, Compute the warping path for subsequence dynamic time warping with
    step sizes {(1, 1), (2, 1), (1, 2)}

    Notebook: C7/C7S2_SubsequenceDTW.ipynb

    Args:
        D: Accumulated cost matrix

    Returns
        P: Warping path (list of index pairs)
    """
    N, M = D.shape
    n = N - 1
    m = D[N - 1, :].argmin()
    P = [(n, m)]

    while n > 1:
        if m == 0:
            cell = (n - 1, 0)
        else:
            val = min(D[n-1, m-1], D[n-2, m-1], D[n-1, m-2])
            if val == D[n-1, m-1]:
                cell = (n-1, m-1)
            elif val == D[n-2, m-1]:
                cell = (n-2, m-1)
            else:
                cell = (n-1, m-2)
        P.append(cell)
        n, m = cell
    P.reverse()
    P = np.array(P)
    P[:, 0] -= 1
    P[:, 1] -= 2
    return P
