"""
ulog2pandas converter
"""

import os
import tempfile
import re
import glob
import numpy as np

import pandas
import pyulog

#pylint: disable=no-member

def ulog2pandas(ulog_filename, verbose=False):
    """
    Convert ulog to pandas dataframe.
    """

    pyulog.ulog2csv.convert_ulog2csv(
        ulog_filename, '', tempfile.tempdir, ',')
    log_name = os.path.splitext(os.path.basename(ulog_filename))[0]
    data = None
    glob_expr = '{:s}*.csv'.format(
        os.path.join(tempfile.gettempdir(), log_name))

    # column naming
    d_col_rename = {
        '[': '_',
        ']': '_',
    }
    col_rename_pattern = re.compile(
        r'(' + '|'.join([re.escape(key) for key in d_col_rename.keys()]) + r')')

    for file in sorted(glob.glob(glob_expr)):
        if verbose:
            print('processing', file)
        file_name = os.path.splitext(os.path.basename(file))[0]
        topic_name = file_name.replace(log_name + '_', '')

        # read data
        data_new = pandas.read_csv(file, index_col=0)
        data_new.columns = [
            topic_name + '_' + col_rename_pattern.sub(
                lambda x: d_col_rename[x.group()], col)
            for col in data_new.columns
        ]

        # append
        if data is None:
            data = data_new
        else:
            data = data.append(data_new)

    # indexing
    data.index = np.array(data.index/1.0e6, dtype=np.float32)
    data.index_name = 't, sec'
    if verbose:
        print(log_name, 'data loaded')
    return data

def time_range(data, time_start, time_end):
    """
    Extract a time range of data.
    """
    data1 = data[data.index >= time_start]
    return data1[data1.index <= time_end]

#  vim: set et fenc=utf-8 ff=unix sts=0 sw=4 ts=4 :
