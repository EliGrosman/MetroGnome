"""
Module: LibFMP.B.B_Annotation
Author: Frank Zalkow, Meinard Mueller
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

This file is part of the FMP Notebooks (https://www.audiolabs-erlangen.de/FMP).
"""

import pandas as pd

def read_csv(fn, header=True, add_label=False):
    """Reads a CSV file

    Args:
        fn: Filename
        header: Boolean
        add_label: Add column with constant value of `add_label`

    Returns:
        df: Pandas DataFrame
    """
    df = pd.read_csv(fn, sep=';', keep_default_na=False, header=0 if header else None)
    if add_label:
        assert 'label' not in df.columns, 'Label column must not exist if `add_label` is True'
        df = df.assign(label=[add_label] * len(df.index))
    return df


def write_csv(df, fn, header=True):
    """Writes a CSV file

    Args:
        df: Pandas DataFrame
        fn: Filename
        header: Boolean
    """
    df.to_csv(fn, sep=';', index=False, quoting=2, header=header)
