# Libraries
import pickle
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import logging

logger = logging.getLogger("journal")

def get_engine(path):
    """Get a sql engine

    Args:
        path (str, Pathlib): path to the database to open 

    Returns:
        engine: engine
    """

    #Conversion to a string if necessary
    if isinstance(path, Path):
        path = str(path)

    return create_engine(f'sqlite:///{path}')

def save_sql(df, path, sql_table="power", if_exists="replace"):
    """Save a dataframe in a sql database

    Args:
        df (pd.DataFrame): dataframe
        path (Path): path to the database file
        sql_table (str, optional): name of the table. Defaults to "power".
        if_exists (str, optional): action if the table already exists. Defaults to "replace".
    """

    try:
        # Get an engine
        engine = get_engine(path)
        
        # Connect to the engine
        with engine.connect() as sql_connection:
            logger.debug(f"engine connected")

            # Save the database
            df.to_sql(sql_table, sql_connection, 
                if_exists=if_exists,
                index_label="longdate",
                index=True)

            logger.debug(f"database saved to {path}")

    except Exception as exce:
        logger.error(f"unable to save the database to {path}")

def load_sql(path, sql_table="power"):
    """Load a sql database in a dataframe

    Args:
        path (Path): path to the database file
        sql_table (str, optional): name of the table. Defaults to "power".

    Returns:
        pd.DataFrame: dataframe
    """

    try:
        # Get an engine
        engine = get_engine(path)

        # Connect to the engine
        with engine.connect() as sql_connection:
            logger.debug(f"engine connected to {path}")

            df = pd.read_sql(sql_table, sql_connection, index_col="longdate")
            
            logger.debug(f"database loaded from {path}")

        return df

    except Exception as exce:
        logger.error(f"unable to load the database from {path} : {exce}")
        return pd.DataFrame()

def save_model(model, name, folder=None):
    """Save the Prophet model in a pkl file

    Args:
        model (Prophet): Prophet model to store
        name (str): name of the model
        folder (Path, optional): location of the store. Defaults to None.
    """

    # Path to the pkl file
    model_pkl = Path(folder, f"{name}.pkl")

    # Save the model in the pkl file
    with open(model_pkl, "wb") as f:
        pickle.dump(model, f)

    logger.debug(f"model {name} saved to {model_pkl}")

def load_model(name, folder=None):
    """Load a model stored in a pkl file

    Args:
        name (str): name of the model to load
        folder (Path, optional): location of the store. Defaults to None.

    Returns:
        _type_: _description_
    """

    # Path to the pkl file
    model_pkl = Path(folder, f"{name}.pkl")

    # Load the model saved in the pkl file
    with open(model_pkl, 'rb') as f:
        model = pickle.load(f)
    
    logger.debug(f"model {name} loaded from {model_pkl}")

    return model