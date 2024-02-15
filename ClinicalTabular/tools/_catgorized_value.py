from __future__ import annotations
import ast
import pandas as pd
from tqdm import tqdm

def assign_age_group(age):
    if age <= 2:
        return '0-2'
    elif age <= 6:
        return '2-6'
    elif age <= 12:
        return '6-12'
    elif age <= 18:
        return '12-18'
    elif age <= 30:
        return '18-30'
    elif age <= 50:
        return '30-50'
    elif age <= 70:
        return '50-70'
    elif age <= 90:
        return '70-90'
    else:
        return '90+'
    
def assign_ige_group(ige):
    if pd.isnull(ige):
        return None
    if ige == 0:
        return 0
    elif ige <= 0.7:
        return 1
    elif ige <= 3.5:
        return 2
    elif ige <= 17.5:
        return 3
    elif ige <= 50:
        return 4
    elif ige <= 100:
        return 5
    elif ige > 100:
        return 6
    else:
        return None




def _check_ranges_complete_and_non_overlapping(norm_ranges):
    # 检查每个性别的范围是否互不重合且覆盖全集
    for gender, ranges in norm_ranges.items():
        sorted_ranges = sorted(ranges.keys(), key=lambda x: x[0])
        last_end = 0
        for age_range in sorted_ranges:
            start, end = age_range[0], age_range[1] if len(age_range) > 1 else float('inf')
            if start < last_end or (last_end != 0 and start > last_end):
                return False
            last_end = end
        if last_end != float('inf'):
            return False
    return True




def check_abnormal(df: pd.Dataframe, col_age: str, col_gender: str, col_value_list: str | list, norm_ranges: dict, suffix:str='_分类')->pd.DataFrame: 
    '''
    params:
        df: dataframe
        col_age: column name of age (str)
        col_gender: column name of gender (str)
        col_value_list: column name of value to be checked (str or list of str)
        norm_ranges: dict of norm ranges (dict)
            - if same for all, the key should be 'all'
            - else column name should be the key 
        suffix: suffix of the new column (str) default: '_分类'
    return:
        df: dataframe with abnormal classification column added (pd.DataFrame)
    '''
    if isinstance(col_value_list, str):
        col_value_list = [col_value_list]
    for col_value in tqdm(col_value_list,total=len(col_value_list) ,desc='processing test value'):
        
        if col_value not in df.columns:
            raise Exception('column name %s not exists' % col_value)
        
        if col_value not in norm_ranges:
            if 'all' in norm_ranges.keys() and len(norm_ranges) == 1:
                norm_ranges[col_value] = norm_ranges['all']
            else:
                raise Exception('norm range for %s not exists' % col_value)
        if col_age not in df.columns:
            raise Exception('column name %s not exists' % col_age)
        if col_gender not in df.columns:
            raise Exception('column name %s not exists' % col_gender)
        # 添加一个新列来存储检验结果的分类
        col_result = col_value + suffix
        df[col_result] = 0  # 默认设置为0（正常）
        print(f"processing {col_value} and generating new column {col_result}")
        norm_range = norm_ranges[col_value]
        for gender, age_ranges in norm_range.items():
            norm_range[gender] = {ast.literal_eval(k): ast.literal_eval(v) for k, v in age_ranges.items() if isinstance(k, str) and isinstance(v, str)}
        
        # 检查年龄范围是否完整且互不重叠
        if not _check_ranges_complete_and_non_overlapping(norm_range):
            raise Exception('age ranges are not complete or overlapping')
        print(f"get norm range for {col_value} done")
        for index, row in tqdm(df.iterrows(), total=len(df), desc=f'processing each row for {col_value}'):
            age = row[col_age]
            gender = row[col_gender]
            gender = gender.replace("男","male").replace("女","female")
            test_value = row[col_value]

            # 查找匹配的年龄范围
            matched = False
            if "all" in norm_range:
                for age_range, (min_normal, max_normal) in (norm_range['all'].items()):
                    if age >= age_range[0] and (len(age_range) == 1 or age < age_range[1]):
                        matched = True
                        if test_value < min_normal:
                            df.at[index, col_result] = -1
                        elif test_value > max_normal:
                            df.at[index, col_result] = 1
                        break
            elif 'male' in norm_range and 'female' in norm_range:
                for age_range, (min_normal, max_normal) in norm_range[gender].items():
                    if age >= age_range[0] and (len(age_range) == 1 or age < age_range[1]):
                        matched = True
                        if test_value < min_normal:
                            df.at[index, col_result] = -1  # 偏小
                        elif test_value > max_normal:
                            df.at[index, col_result] = 1   # 偏高
                        break

            if not matched:
                df.at[index, col_result] = None  # 未知或不适用
    
    return df

