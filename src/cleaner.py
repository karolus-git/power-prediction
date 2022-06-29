# Libraries
import pandas as pd
import unidecode

# Modules
import selector

def clean_nan_rows(df, inplace=True):
    """Clean rows containing any Nan

    Args:
        df (pd.DataFrame): dataframe
        inplace (bool, optional): change the original dataframe directly. Defaults to True.
    """

    df.dropna(axis=0, how="any", inplace=inplace)

def clean_power(df, columns=[], data_from="csv"):

    if data_from == "csv":
        df.index = pd.DatetimeIndex(pd.to_datetime(df.Date + " " +df.Heure))       
        df.columns = [unidecode.unidecode(column.lower()).replace(" (mw)", "") for column in df.columns]
        df = df.rename(columns={"prevision j-1": "prevision_j1"})
        
    elif data_from == "api":
        df.index = pd.DatetimeIndex(pd.to_datetime(df.date + " " +df.heure))

    df.index.name = "longdate"

    df = selector.get_columns(df, columns=columns)
    df = df.groupby(pd.Grouper(axis=0, freq="H")).mean()

    df = df.sort_index()

    return df


def clean_weather(df, columns=[], data_from="csv"):
    
    if data_from == "csv":
        df = df.groupby("Date").mean()
        df.columns = ["code", "wspd", "sun"]
        df.index.name = "longdate"

    elif data_from == "api":        
        df = df.groupby("date").mean()
        df.columns = ["sun", "wspd"]

    df.index = pd.DatetimeIndex(pd.to_datetime(df.index, format = '%Y-%m-%dT%H:%M:%S%z', utc=True).strftime('%Y-%m-%d %H:%M:%S'))
    df = selector.get_columns(df, columns=columns)

    df = df.sort_index()

    return df
    
    
def clean_temp(df, columns=[], data_from="csv"):

    
    if data_from == "csv":
        df = df.groupby("Date").mean()
        df.columns = ["code", "tmin", "tmax", "tmoy"]
        df.index = pd.DatetimeIndex(pd.to_datetime(df.index, format = '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'))
    
    elif data_from == "api":
        df = df.groupby("date").mean()

    df.index.name = "longdate"
    df = df.loc[:, columns]

    df = df.sort_index()

    return df 