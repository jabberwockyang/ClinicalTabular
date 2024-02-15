from __future__ import annotations
import pandas as pd
from tqdm import tqdm
 

def replace_col(df: pd.DataFrame,col1: str,col2: str) -> pd.DataFrame:
    """
    Replace NaN in col1 with values from col2
    If both col1 and col2 are non-null in a row, print a warning and do not replace
    args:
        df: dataframe
        col1: column name of col1
        col2: column name of col2
    return:
        df: dataframe with col1 replaced by col2
    """
    # Check if there are any rows where both columns are non-null
    if col1 not in df.columns:
        raise ValueError(f'Column {col1} not found in dataframe')
    if col2 not in df.columns:
        raise ValueError(f'Column {col2} not found in dataframe')
    
    both_non_null = df[[col1,col2]].notnull().all(axis=1)
    if not both_non_null.any():
        # Replace NaN in '嗜酸粒绝对计数' with values from '嗜酸粒绝对值'
        df[col1] = df[col1].fillna(df[col2])
        df.drop(columns=[col2], inplace=True)
    else:
        for index, is_both_non_null in both_non_null.iteritems():
            if is_both_non_null:
                print(f"Not all null in row {index}")
        print(f"Cannot replace {col1} with {col2} because there are rows where both are non-null")
    return df

import pandas as pd

def split_diagnoses(df, column_name):
    """
    split diagnoses in a column into multiple rows

    args:
    df: pandas.DataFrame
    column_name: 

    return:
    new_df: pandas.DataFrame
    """
    new_rows = []

    # iterate over rows in dataframe
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Splitting diagnoses", position=0, leave=True):
        if pd.isna(row[column_name]): # skip rows with no diagnosis
            continue
        diagnoses = row[column_name].split('，') # split diagnoses by comma
        for diagnosis in diagnoses:
            new_row = row.copy()
            new_row[column_name] = diagnosis
            new_rows.append(new_row)

    print('Splitting diagnoses done, generating new dataframe')
    new_df = pd.DataFrame(new_rows).reset_index(drop=True)

    return new_df

def remove_suspicous_diagnosis(df:pd.DataFrame, column_name:str):
    '''
    remove rows with suspicious diagnosis
    args:
        df: pandas.DataFrame
        column_name: str
    return:
        df: pandas.DataFrame
    '''
    df = df[~df[column_name].str.contains('?')]
    return df

def subset_top_features(df, column_name, top_n):
    """
    Subset a DataFrame based on the most frequent features in a specified column.

    :param df: Pandas DataFrame.
    :param column_name: The name of the column to analyze.
    :param top_n: The number of most frequent features to consider.
    :return: A subset of the original DataFrame.
    """

    # Ensure the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    # Get the top 'top_n' most frequent features in the column
    top_features = df[column_name].value_counts().head(top_n).index
    print(df[column_name].value_counts().head(20))
    print(f"get top {top_n} features in column {column_name}")
    # Subset the DataFrame to include only rows with these top features
    subset_df = df[df[column_name].isin(top_features)]

    return subset_df