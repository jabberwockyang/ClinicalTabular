from __future__ import annotations
import hashlib
import pandas as pd

def generate_patient_ids(df: pd.DataFrame, colnames:list =['姓名', '性别', '出生年月'],id_colname:str = 'patient_id')->pd.DataFrame:
    """
    Generate patient ids based on the combination of the columns in colnames.
    args:
        df: pd.DataFrame
        colnames: list of colname to be identified. default ['姓名', '性别', '出生年月']
        id_colname: name of the id column. default 'patient_id'
    return:
        df: pd.DataFrame

    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a pandas DataFrame')
    if not isinstance(colnames, list):
        raise TypeError('colnames must be a list')
    patient_ids = []
    for i, row in df.iterrows():
        combined_string = '-'.join([str(row[col]) for col in colnames])
        hash_object = hashlib.sha256(combined_string.encode())
        patient_id = hash_object.hexdigest()
        patient_ids.append(patient_id)
    df[id_colname] = patient_ids
    return df