from __future__ import annotations
import pandas as pd

def calculate_non_null_percentages(df: pd.DataFrame, ascending: bool =False):
    '''
    df: pandas.DataFrame
    ascending: bool
    return:
        non_null_percentages_df: pandas.DataFrame
    '''
    
    non_null_percentages = df.notnull().mean() * 100
    non_null_percentages_df = non_null_percentages.to_frame(name='Non-Null Percentage')
    non_null_percentages_df.sort_values(by='Non-Null Percentage', inplace=True, ascending=ascending)
    
    return non_null_percentages_df
