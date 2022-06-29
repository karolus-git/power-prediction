# Libraries
from datetime import datetime

def date(input_date):
    """Try to convert a string date to a datetime

    *Ugly ! Please find a other solution*
    Args:
        input_date (str): date as a string

    Returns:
        datetime: date as a datetime

    """
    if isinstance(input_date,  str):
        try :
            return datetime.strptime(input_date, "%Y-%m-%d %H:%M")
        except:
            try :
                return datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
            except:
                try :
                    return datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    try :
                        return datetime.strptime(input_date, "%Y-%m-%d")
                    except:
                        try :
                            return datetime.strptime(input_date, "%Y-%m-%dT%H:%M")
                        except:
                            try :
                                return datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S.%f")
                            except:
                                try :
                                    return datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S.%f")
                                except:
                                    return input_date
                                    
    return input_date