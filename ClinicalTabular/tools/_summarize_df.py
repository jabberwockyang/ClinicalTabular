from __future__ import annotations
import pandas as pd
from tqdm import tqdm

def summarize_data(df: pd.DataFrame , group_cols: list, summarization_methods: dict):
    '''
    args:
        df: dataframe
        group_cols: list of column names to group by
        summarization_methods: dictionary of column names and summarization methods

            - format: { 'method': ['col1', 'col2', 'col3'],
                        'method2': ['col3', 'col4', 'col5']}

            - method can be 'average', 'sum', 'min', 'max', 'median', 'most frequent', 'original'
                - for 'average', 'sum', 'min', 'max', 'median' methods, only numeric columns are supported
                - for 'most frequent' method, only categorical columns are supported

            - example: {'original': ['patient_id'],
                        'most frequent':['diagnosis'],
                        'max': df.select_dtypes(include=['float64', 'int64']).columns
                        }
                
    return:
        summarized_df: dataframe with summarized data
    
    '''
    # Group the DataFrame by the specified columns
    grouped = df.groupby(group_cols)

    # Initialize a dictionary to hold the summarized data
    summary_data = {}

    # Iterate over each column and apply the specified summarization method
    for method, cols in summarization_methods.items():
        if isinstance(cols,str):
            cols = [cols]
        for col in tqdm(cols, desc=f"Summarizing specified columns with method {method}"):
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
            if method == 'original':
                if col in group_cols:
                    summary_data[col] = grouped[col].first()
                else:
                    raise ValueError(f"Column {col} cannot be summarized with 'original' method")
            elif method == 'first':
                if col in df.columns:
                    summary_data[col] = grouped[col].first()
                else:
                    raise ValueError(f"Column {col} cannot be summarized with 'original' method")
 
            elif method == 'most frequent':
                summary_data[col] = grouped[col].agg(lambda x: x.mode()[0] if not x.empty else None)
            elif method in ['average', 'sum', 'min', 'max', 'median']:
                # Convert non-numeric values to NaN for numeric summarization methods
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if method == 'average':
                    summary_data[col] = grouped[col].mean()
                elif method == 'sum':
                    summary_data[col] = grouped[col].sum()
                elif method == 'min':
                    summary_data[col] = grouped[col].min()
                elif method == 'max':
                    summary_data[col] = grouped[col].max()
                elif method == 'median':
                    summary_data[col] = grouped[col].median()
            elif method == 'count':
                summary_data[col] = grouped[col].count()
            else:
                raise ValueError(f"Unsupported summarization method: {method}")

    # Combine the summarized data into a new DataFrame
    summarized_df = pd.DataFrame(summary_data)

    return summarized_df

# def summarize_data_optimized(df, group_cols, summarization_methods):
#     # Check for invalid columns before processing
#     invalid_cols = set(sum(summarization_methods.values(), [])) - set(df.columns)
#     if invalid_cols:
#         raise ValueError(f"Columns {invalid_cols} not found in DataFrame")

#     # Group the DataFrame by the specified columns
#     grouped = df.groupby(group_cols)

#     # Convert columns to numeric where necessary
#     for method, cols in tqdm(summarization_methods.items(), desc="transforming specified columns into numeric type"):
#         if method in ['average', 'sum', 'min', 'max', 'median']:
#             df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

#     # Initialize a dictionary to hold the summarized data
#     summary_data = {}

#     # Iterate over each column and apply the specified summarization method
#     for method, cols in tqdm(summarization_methods.items(), desc="Summarizing specified columns"):
#         for col in cols:
#             if method == 'original':
#                 # For 'original' method, select the first value in each group
#                 summary_data[col] = grouped[col].first()
#             elif method == 'most frequent':
#                 summary_data[col] = grouped[col].agg(pd.Series.mode).iloc[:, 0]
#             elif method == 'average':
#                 summary_data[col] = grouped[col].mean()
#             elif method == 'sum':
#                 summary_data[col] = grouped[col].sum()
#             elif method == 'min':
#                 summary_data[col] = grouped[col].min()
#             elif method == 'max':
#                 summary_data[col] = grouped[col].max()
#             elif method == 'median':
#                 summary_data[col] = grouped[col].median()
#             elif method == 'count':
#                 summary_data[col] = grouped[col].count()
#             else:
#                 raise ValueError(f"Unsupported summarization method: {method}")

#     # Combine the summarized data into a new DataFrame
#     summarized_df = pd.DataFrame(summary_data)

#     return summarized_df

