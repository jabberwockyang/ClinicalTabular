from __future__ import annotations
from ._translate import BaiduTranslate

def get_map_dict_colnames(df):
    """
    Get a dictionary mapping the original column names to new column names.

    :param df: Pandas DataFrame.
    :return: A dictionary mapping original column names to new column names.
    """

    # Get the column names
    column_names = df.columns
    bt = BaiduTranslate(from_lang = 'zh',to_lang ='en')
    # Create a dictionary mapping original column names to new column names
    map_dict = {column_name: bt.translator(column_name).replace(' ', '_').lower() for column_name in column_names}

    return map_dict


def get_map_dict_catego(df, column_name):
    """
    Get a dictionary mapping the original values in a column to new values.

    :param df: Pandas DataFrame.
    :param column_name: The name of the column to analyze.
    :return: A dictionary mapping original values to new values.
    """

    # Ensure the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    # Get the unique values in the column
    unique_values = df[column_name].unique()

    bt = BaiduTranslate(from_lang = 'zh',to_lang ='en')
    # Create a dictionary mapping original values to new values
    map_dict = {value: bt.translator(value) for value in unique_values}

    return map_dict