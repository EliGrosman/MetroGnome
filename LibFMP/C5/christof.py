import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from numba import jit
import LibFMP.C3


FMP_COLORMAPS_CW = {
    'FMP_2': colors.ListedColormap([[1, 1, 1], [1, 0.3, 0.3], [1, 0.7, 0.7], [0, 0, 0]])
}

def parse_chord_annotations_numeric(annotations, feature_rate):
    n_frames = np.ceil(annotations.iloc[-1, 1] * feature_rate).astype(int)
    annotations_numeric = np.zeros((24, n_frames))
    chord_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chord_labels += [c + ':min' for c in chord_labels]
    chord_labels_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    chord_labels_flat += [c + ':min' for c in chord_labels_flat]
    for i, (start, end, label) in annotations.iterrows():
        frame_min = np.round(start * feature_rate).astype(int)
        frame_max = np.round(end * feature_rate).astype(int)
        if label != 'N':
            try:
                labelIndex = chord_labels.index(label)
            except:
                labelIndex = chord_labels_flat.index(label)
            annotations_numeric[labelIndex, frame_min:frame_max] = 1
    return annotations_numeric

def generate_template_matrix(templates):
    assert templates.shape[0] == 12, 'input "templatesC" has wrong size!'
    template_matrix = np.zeros((12, 12 * templates.shape[1]))
    for shift in range(12):
        template_matrix[:, shift::12] = np.roll(templates, shift, axis=0)
    return template_matrix

def analysis_template_match(f_chroma, templates, apply_normalization=True, norm_output='2'):
    assert templates.shape[0] == 12, 'input "f_chroma" has wrong size!'
    assert templates.shape[0] == 12, 'input "templates" has wrong size!'
    chroma_normalized = LibFMP.C3.normalize_feature_sequence(f_chroma, norm='2')
    templates_normalized = LibFMP.C3.normalize_feature_sequence(templates, norm='2')
    f_analysis = np.matmul(templates_normalized.T, chroma_normalized)
    if apply_normalization:
         f_analysis = LibFMP.C3.normalize_feature_sequence(f_analysis, norm=norm_output)
    return f_analysis

def viterbi_log_continuous(A, C, B_func_Obs_seq):
    I = A.shape[0]    # number of states
    N = B_func_Obs_seq.shape[1]  # length of observation sequence
    # compute log probabilities
    tiny = np.finfo(0.).tiny
    A_log = np.log(A + tiny)
    C_log = np.log(C + tiny)
    B_func_log = np.log(B_func_Obs_seq + tiny)
    # initialize D and E matrices
    D_log = np.zeros((I, N))
    E = np.zeros((I, N-1))
    D_log[:, 0] = C_log + B_func_log[:, 0]
    # compute D and E in a nested loop
    for n in range(1, N):
        for i in range(I):
            temp_sum = A_log[:, i] + D_log[:, n-1]
            D_log[i,n] = np.amax(temp_sum) + B_func_log[i, n]
            E[i, n-1] = np.argmax(temp_sum)
    max_ind = np.zeros((1, N))
    max_ind[0, -1] = np.argmax(D_log[:, -1])
    # Backtracking
    for n in range(N-2, 0, -1):
        max_ind[0, n] = E[int(max_ind[0, n+1]), n]
    # Convert zero-based indices to state indices
    S_opt = np.squeeze(max_ind.astype(int)+1)
    return S_opt

@jit(nopython=True)
def compute_visualization_array(annotations, analysis):
    true_positives = annotations * analysis
    false_positives = analysis - true_positives
    false_negatives = annotations - true_positives
    results = 3 * true_positives + 2 * false_negatives + 1 * false_positives
    return results

def compute_eval_measures(annotations, results):
    num_true_positives = np.sum(np.min(annotations == results, axis=0))
    num_false_positives = np.sum(results>0, axis=None) - num_true_positives
    num_false_negatives = np.sum(annotations>0, axis=None) - num_true_positives
    precision = num_true_positives / (num_true_positives + num_false_positives)
    recall = num_true_positives / (num_true_positives + num_false_negatives)
    f_measure = 2 * precision * recall / (precision + recall)
    return precision, recall, f_measure

def cyclic_mean(A):
    A_shifted = np.zeros(A.shape)
    A_means = np.zeros(A.shape)
    A_cycle_means = np.zeros(A.shape)
    num_cols = A.shape[0]
    for i in range(num_cols):
        A_shifted[:, i] = np.roll(A[:, i], -i, axis=0)
    A_means = np.tile(np.expand_dims(np.mean(A_shifted, axis=1), axis=1), (1, num_cols))
    for i in range(num_cols):
        A_cycle_means[:, i] = np.roll(np.array(A_means[:, i]), i, axis=0)
    return A_cycle_means

@jit(nopython=True)
def uniform_transition_matrix(self_transition_prob, num_cols):
    off_diag_entries = (1-self_transition_prob)/(num_cols-1)     # rows should sum up to 1
    A_uniform = off_diag_entries * np.ones((num_cols, num_cols))
    np.fill_diagonal(A_uniform, self_transition_prob)
    return A_uniform

def transposition_invariance(A):
    A_inv = np.zeros(A.shape)
    A_inv[0:12, 0:12] = cyclic_mean(A[0:12, 0:12])
    A_inv[0:12, 12:24] = cyclic_mean(A[0:12, 12:24])
    A_inv[12:24, 0:12] = cyclic_mean(A[12:24, 0:12])
    A_inv[12:24, 12:24] = cyclic_mean(A[12:24, 12:24])
    return A_inv

@jit(nopython=True)
def plot_transition_matrix(A, ax=None, xlabel='State $a_j$', ylabel='State $a_i$', title='', clim=[-6, 0], cmap='gray_r'):
    A_log = np.log(A)
    im = ax[0].imshow(A_log, origin='lower', aspect='auto', cmap=cmap)
    im.set_clim([-6, 0])
    plt.sca(ax[0])
    cbar = plt.colorbar(im)
    ax[0].set_xlabel(xlabel)
    ax[0].set_ylabel(ylabel)
    ax[0].set_title(title)
    cbar.ax.set_ylabel('Log probability')
    chroma_label = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chord_label_maj = chroma_label
    chord_label_min = [s + 'm' for s in chroma_label]
    chord_labels = chord_label_maj + chord_label_min
    chord_labels_squeezed = chord_labels.copy()
    for k in [13, 15, 17, 18, 20, 22]:
        chord_labels_squeezed[k] = ''
    ax[0].set_xticks(np.arange(24))
    ax[0].set_yticks(np.arange(24))
    ax[0].set_xticklabels(chord_labels_squeezed)
    ax[0].set_yticklabels(chord_labels)
    return im

def plot_eval_matrix(annotations, analysis, Fs=1, Fs_F=1, T_coef=None, F_coef=None, xlabel='Time (seconds)', ylabel='', title='',
                dpi=72, colorbar=True, colorbar_aspect=20.0, colormap=FMP_COLORMAPS_CW['FMP_2'], clim=[0, 4], ax=None, figsize=(6, 3), **kwargs):
    """Plot an evaluation matrix for showing true positives, false positives, and false negatives

    Parameters
    ----------
    annotations : np.ndarray [shape=(n, m)], real-valued
        The annotation (ground truth) matrix

    analysis : np.ndarray [shape=(n, m)], real-valued
        The analysis (results) matrix

    Fs : int > 0 [scalar]
        Sample rate for axis 1

    Fs_F : int > 0 [scalar]
        Sample rate for axis 0

    T_coef : np.ndarray or None
        Time coeffients. If None, will be computed, based on Fs.

    F_coef : np.ndarray or None
        Frequency coeffients. If None, will be computed, based on Fs_F.

    xlabel : string
        Label for x axis

    ylabel : string
        Label for y axis

    title : string
        Title for plot

    dpi : int
        Dots per inch

    colorbar : boolean
        Create a colorbar.

    colorbar_aspect : float
        Aspect used for colorbar, in case only a single axes is used.

    ax : list of matplotlib.axes.Axes or None
        Either (1.) a list of two axes (first used for matrix, second for colorbar), or (2.) a list with a single axes
        (used for matrix), or (3.) None (an axes will be created).

    figsize : tuple of float
        Width, height in inches

    **kwargs : dict
        Keyword arguments for matplotlib.pyplot.imshow

    Returns
    -------
    fig : matplotlib.figure.Figure or None
        The created matplotlib figure or None if ax was given.

    ax : list of matplotlib.axes.Axes
        The used axes.

    im : matplotlib.image.AxesImage
        The image plot
    """
    X = compute_visualization_array(annotations=annotations, analysis=analysis)
    eval_cmap = colormap
    # eval_bounds = np.array([0, 1, 2, 3, 4])-0.5
    # eval_norm = colors.BoundaryNorm(eval_bounds, eval_cmap.N)
    # eval_ticks = [0, 1, 2, 3]
    # eval_cmap = colors.ListedColormap([[1, 1, 1], [1, 0.3, 0.3], [1, 0.7, 0.7], [0, 0, 0]])
    eval_bounds = np.arange(len(eval_cmap.colors)+1)-0.5
    eval_norm = colors.BoundaryNorm(eval_bounds, eval_cmap.N)
    eval_ticks = np.arange(len(eval_cmap.colors))

    fig = None
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        ax = [ax]
    if T_coef is None:
        T_coef = np.arange(X.shape[1]) / Fs
    if F_coef is None:
        F_coef = np.arange(X.shape[0]) / Fs_F

    if 'extent' not in kwargs:
        x_ext1 = (T_coef[1] - T_coef[0]) / 2
        x_ext2 = (T_coef[-1] - T_coef[-2]) / 2
        y_ext1 = (F_coef[1] - F_coef[0]) / 2
        y_ext2 = (F_coef[-1] - F_coef[-2]) / 2
        kwargs['extent'] = [T_coef[0] - x_ext1, T_coef[-1] + x_ext2, F_coef[0] - y_ext1, F_coef[-1] + y_ext2]
    if 'cmap' not in kwargs:
        kwargs['cmap'] = eval_cmap
    if 'norm' not in kwargs:
        kwargs['norm'] = eval_norm
    if 'aspect' not in kwargs:
        kwargs['aspect'] = 'auto'
    if 'origin' not in kwargs:
        kwargs['origin'] = 'lower'

    im = ax[0].imshow(X, **kwargs)

    if len(ax) == 2 and colorbar:
        cbar = plt.colorbar(im, cax=ax[1], cmap=eval_cmap, norm=eval_norm, boundaries=eval_bounds, ticks=eval_ticks)
    elif len(ax) == 2 and not colorbar:
        ax[1].set_axis_off()
    elif len(ax) == 1 and colorbar:
        plt.sca(ax[0])
        cbar = plt.colorbar(im, aspect=colorbar_aspect, cmap=eval_cmap, norm=eval_norm, boundaries=eval_bounds, ticks=eval_ticks)

    cbar.ax.set_yticklabels(['', 'FP', 'FN', 'TP'])
    ax[0].set_xlabel(xlabel)
    ax[0].set_ylabel(ylabel)
    ax[0].set_title(title)

    if fig is not None:
        plt.tight_layout()

    return fig, ax, im
