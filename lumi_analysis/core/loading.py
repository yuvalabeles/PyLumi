import pandas as pd


def load_files(path_lst):
    # Load files:
    dfs = []
    for p in path_lst:
        dfs.append(pd.read_csv(p, header=1, index_col=0))

    return dfs
