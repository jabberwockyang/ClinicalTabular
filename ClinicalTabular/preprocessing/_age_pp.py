from __future__ import annotations
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
tqdm.pandas(desc="Processing")

def _to_pddatetime(date_str: str | float | int | pd.Timestamp) -> pd.Timestamp | pd.NaT:
    """
    Convert date string to pandas datetime
    if date_str is already pandas datetime, return date_str
    if date_str is NaN, return NaN
    if date_str is float or integer, convert to string and return pandas datetime
    if date_str is string, return pandas datetime
    """
    if isinstance(date_str, pd.Timestamp):
        return date_str
    elif pd.isna(date_str):
        return pd.NaT
    elif isinstance(date_str, float):
        date_str = str(int(date_str))
    elif isinstance(date_str, int):
        date_str = str(date_str)

    if isinstance(date_str, str):
        date_str = date_str.replace('.0', '')
        numbers = re.sub("[^0-9]", "", date_str)

        # Determine the format based on the length of numbers
        if len(numbers) == 6:
            # Assuming format yy-mm-dd
            year_prefix = '19' if int(numbers[:2]) > 25 else '20'
            formatted_date = f'{year_prefix}{numbers[:2]}-{numbers[2:4]}-{numbers[4:6]}'
        elif len(numbers) == 8:
            # Assuming format yyyy-mm-dd
            formatted_date = f'{numbers[:4]}-{numbers[4:6]}-{numbers[6:8]}'
        else:
            print(f'Unexpected format: {numbers}, returning NaT')
            return pd.NaT

        # Convert to pandas datetime
        return pd.to_datetime(formatted_date, format='%Y-%m-%d', errors='coerce')

    else:
        print(f'Unexpected type: {type(date_str)},returning NaT')
        return pd.NaT

def datetime_conversion(df: pd.DataFrame, date_col: str | list) ->pd.DataFrame:
    """
    Convert date string to pandas datetime
    args:
        df: dataframe
        date_col: column name of date
    return:
        df: dataframe with date_col converted to pandas datetime
    """
    if isinstance(date_col, str):
        date_col = [date_col]
    if isinstance(date_col, list):
        for col in date_col:
            print(f'Converting {col} to pandas datetime')
            if col not in df.columns:
                raise ValueError(f'Column {col} not found in dataframe')
            else:
                try:
                    df[col] = df[col].progress_apply(_to_pddatetime)
                except Exception as e:
                    print(f'Error in datetime_conversion: {e}')
        return df
    else:
        raise ValueError(f'Unexpected type: {type(date_col)}')


def _age_conversion(age_str: str | float | int, unit_of_year:str = None, unit_of_month :str = None) -> float | np.nan:
    """
    Convert age string to numeric age
    if age_str is NaN, return NaN
    if age_str is already numeric, return age_str
    if age_str is string, return numeric age
    """
    
    if  pd.isna(age_str):
        return np.nan
    elif isinstance(age_str,(int,float)):
        return age_str

    elif isinstance(age_str, str):
        # find unit of age 
        if re.findall("年",age_str) or re.findall("岁",age_str) or (unit_of_year and re.findall(unit_of_year,age_str)) or re.findall("Y",age_str) or re.findall("y",age_str) :
            return pd.to_numeric(re.sub("[^0-9]", "", age_str), errors='coerce')
        if re.findall("月",age_str) or (unit_of_month and re.findall(unit_of_month, age_str)) or re.findall("M",age_str) or re.findall("m",age_str):
            return pd.to_numeric(re.sub("[^0-9]", "", age_str), errors='coerce')/12
        else:
            print("no unit of age found, please check the input string, retruning year as default")
            return pd.to_numeric(re.sub("[^0-9]", "", age_str), errors='coerce')
    else:
        print(f'Unexpected type: {type(age_str)},returning NaN')
        return pd.NaN


from dateutil.relativedelta import relativedelta

def _date_minus_age(exam_date: pd.Timestamp| pd.NaT, age:float| pd.NaT) -> pd.Timestamp | pd.NaT:
    if pd.isna(exam_date) or pd.isna(age):
        print(f'Na value in : {exam_date,type(exam_date)} and {age,type(age)}, returning NaT')
        return pd.NaT
    elif isinstance(exam_date, pd.Timestamp) and isinstance(age, (float, int)):
        if age > 150:
            print(f'age > 150: {age}, try convert to DOB')
            birth_date = _to_pddatetime(age)
            return birth_date
        
        try:
            birth_date = exam_date - relativedelta(years=int(age))
        except Exception as e:
            print(f'Error in relativedelta: when minus {age} from {exam_date}, {e}, returning NaT')
            return pd.NaT
        # Ensure birth_date is within pandas Timestamp bounds
        if pd.Timestamp.min <= birth_date <= pd.Timestamp.max:
            return birth_date
        else:
            print(f'birth_date out of bounds: {birth_date}, returning NaT')
            return pd.NaT
    else:
        print(f'Unexpected type: {type(exam_date)} and {type(age)}, returning NaT')
        return pd.NaT


def dob_calculation(df: pd.DataFrame, age_col: str, date_col: str,colname_dob: str) -> pd.DataFrame:
    """
    Calculate dob from age and date
    args:
        df: dataframe
        age_col: column name of age
        date_col: column name of date
        colname_dob: column name of dob to be added
    return:
        df: dataframe with dob column
    """
    if age_col not in df.columns:
        raise ValueError(f'Column {age_col} not found in dataframe')
    if date_col not in df.columns:
        raise ValueError(f'Column {date_col} not found in dataframe')
    
    if not isinstance(df[age_col].iloc[0], (float, int)):
        print(f'Deteceted non-numeric type in age_col. Converted {age_col} to numeric, default unit: year')
        df[age_col] = df[age_col].apply(_age_conversion)
        
    if not isinstance(df[date_col].iloc[0], pd.Timestamp):
        print(f'Deteceted non-datetime type in date_col. Converted {date_col} to pandas datetime')
        df[date_col] = df[date_col].apply(_to_pddatetime)
    
    try:
        df[colname_dob] = df.apply(lambda x: _date_minus_age(x[date_col], x[age_col]), axis=1)
        return df
    except Exception as e:
        print(f'Error in age_calculation: {e}')