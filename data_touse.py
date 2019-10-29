import pandas as pd
temp_df = pd.read_csv('./output/df_final.csv', sep='\t')

with pd.option_context('display.max_rows', 20, 'display.max_columns', None):
    print(temp_df)
