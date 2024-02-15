from __future__ import annotations
import pandas as pd
import warnings
from tqdm import tqdm


def fillna_with_group_stats(df, col_to_ref, col_to_fill, stat_method):
    '''
    使用基于特定列分组的统计数据填充缺失值。
    args:
        df: DataFrame
        col_to_ref: 用于分组的参考列的名称
        col_to_fill: 要填充的列的名称
        stat_method: 统计方法 (例如 'mean', 'median')
    return:
        df: 修改后的 DataFrame
    '''
    if isinstance(col_to_fill, str):
        col_to_fill = [col_to_fill]
    warnings.filterwarnings("ignore", message="Mean of empty slice")

    grouped = df.groupby(col_to_ref)
    for col in tqdm(col_to_fill, desc=f"Filling {stat_method}"):
        if stat_method == 'mean':
            fill_values = grouped[col].transform('mean')
        elif stat_method == 'median':
            fill_values = grouped[col].transform('median')
        else:
            raise ValueError("Unsupported stat_method. Use 'mean' or 'median'.")
        df.loc[:, col] = df[col].fillna(fill_values)
    return df
