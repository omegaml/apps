import os
import pandas as pd
import requests
import joblib

def read_data(records=100):
    """ read latest N records from machine API
    
    Args:
        records (int): the number of records, defaults to 100
        
    Returns:
        df (pd.DataFrame): the dataframe with columns
        
           dt: datetime of the value
           value: a sensor value
    """
    resp = requests.get(f'http://localhost:5000/query/{records}')
    data = resp.json()

    df = pd.DataFrame({
        'dt': pd.to_datetime([v[0] for v in data['values']]),
        'value': [v[1] for v in data['values']],
    })
    return df.set_index('dt')

def fix(series):
    """ fix the series to match the model API
    
    Args:
        series (pd.Series): the series to reshape
        
    Return:
        series with shape (n_samples, n_features)
    """
    return series.values.reshape((-1, 1))

def load_model(name):
    """ load a model
    
    Args:
        name (str): the path/name of the model
        
    Returns:
        the model
    """
    name = name.replace('/', os.path.sep)
    with open(name, 'rb') as fin:
        model = joblib.load(fin)
    return model

def save_model(model, name):
    """ save a model
    
    Args:
        name (str): the path/name of the model
        
    Returns:
        None
    """
    name = name.replace('/', os.path.sep)
    with open(name, 'wb') as fout:
        joblib.dump(model, fout)