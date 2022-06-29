
def get_columns(df, columns=[]):
    """Select columns of the dataframe 

    Args:
        df (pd.Dataframe): datafrale
        columns (list, optional): columns to select. Defaults to [].

    Returns:
        _type_: _description_
    """
    # If columns are given, we return only the selected columns of the dataframe. Otherwise, the full dataframe is returned
    return df.loc[:, columns] if columns else df

def get_dates(df, start=None, end=None, date=None):
    """Select indexes of the dataframe according to the input variables

    * if only start is given, the end date will be the maximal date of the index
    * if only end is given, the start date will be the minimal date of the index
    * if a date is given, the date is searched in the dataframe

    Args:
        df (pd.DataFrame): dataframe
        start (datetime, optional): minimal date to find. Defaults to None.
        end (datetime, optional): maximal date to find. Defaults to None.
        date (datetime, optional): date. Defaults to None.

    Returns:
        pd.DataFrame: selected part of the dataframe
    """

    # Start and end are given
    if (start) and (end):
        return df.iloc[(df.index < end) & (df.index >= start)] 
    # Only end is given
    elif (not start) and (end):
        return df.iloc[df.index < end] 
    # Only start is given
    elif (start) and (not end):
        return df.iloc[df.index >= start] 
    # A deta is given
    elif date:
        return df.iloc[df.index == date] 
    # If nothing is given, we return the dataframe without selection
    else:
        return df
