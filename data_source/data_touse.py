import pandas as pd
import numpy as np

# temp_df = pd.read_csv('../outputs/df_final.csv', sep='\t')
#
# with pd.option_context('display.max_rows', 20, 'display.max_columns', None):
#     print(temp_df)


def data_github_0():
    df_raw = pd.read_csv('../outputs/df_final.csv', sep='\t')
    df_raw = df_raw.drop(columns=['name', 'url', 'pullRequests', 'totalIssues'])

    # df_raw = df_raw.head(206)       # for unarchived part
    # df_raw = df_raw.tail(200)       # for archived part

    last_col = 'stars'
    # last_col = 'commits'
    # last_col = 'activities'

    cols = list(df_raw.columns.values)
    cols.pop(cols.index(last_col))
    df_adjust = df_raw[cols+[last_col]]

    return df_adjust


if __name__ == '__main__':
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(data_github_0())
