import pandas as pd


def latex_print_detail(func):
    s = func.__name__[5:]
    df = func()
    attr_nums = len(df.columns)
    print('\multirow{%d}{*}{\\begin{sideways}%s\\end{sideways}\\begin{sideways}(%d)\\end{sideways}}' % (
    attr_nums, s, df.shape[0]))
    for attr in df.columns:
        name = attr
        m = df[attr].min()
        M = df[attr].max()
        avg = df[attr].mean()
        sd = df[attr].std()
        print("& %s & %.0f & %.0f & %.1f & %.1f\\\\" % (name, m, M, avg, sd))
    print('\\hline')

