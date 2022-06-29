# Libraries
import argparse
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import logging
import os

# Modules
import journal
import models
import collector
import cleaner
import selector
import store

# Constants
from config import COL_POWER
from config import COL_TEMP
from config import COL_WEATHER
from config import DATASET_RAW_FOLDER
from config import DATASET_PROCESSED_FOLDER
from config import MODELS_FOLDER
from config import NAME_CSV_POWER
from config import NAME_CSV_TEMP
from config import NAME_CSV_WEATHER
from config import NAME_DB_EXPANDED
from config import LINK_CSV_POWER
from config import LINK_CSV_TEMP
from config import LINK_CSV_WEATHER 

logger = journal.init_journal()

class Pipeline():
    """The Pipeline is there to :

    * get the data : download or importing
    * process the data : clean and joining
    * serve the data : shrink and select


    """
    def __init__(self,):
        
        self.models = {
            "prophet_time" :{
                "name" : "Prophet based on time series",
                "model" : None,
                "end_training" : "2019-12-31",
                "target" : "consommation",
                "regressors" : [],
                "trained" : False,
            },
            "prophet_temp" :{
                "name" : "Prophet with temperatures",
                "model" : None,
                "end_training" : "2021-12-31",
                "target" : "consommation",
                "regressors" : ["tmoy",],
                "trained" : False,
            },
            "prophet_weather" :{
                "name" : "Prophet with weather",
                "model" : None,
                "target" : "consommation",
                "end_training" : "2021-12-31",
                "regressors" : ["tmoy", "tmax", "tmin", "wspd", "sun"],
                "trained" : False,
            }
        }

        self.create_folders()

        self.path_csv_power = Path(DATASET_RAW_FOLDER, NAME_CSV_POWER)
        self.path_csv_temp = Path(DATASET_RAW_FOLDER, NAME_CSV_TEMP)
        self.path_csv_weather = Path(DATASET_RAW_FOLDER, NAME_CSV_WEATHER)

        self.path_db_expanded = Path(DATASET_PROCESSED_FOLDER, NAME_DB_EXPANDED)

    def create_folders(self,):
        """Create static folders
        """

        for path in [DATASET_RAW_FOLDER, DATASET_PROCESSED_FOLDER]:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.debug(f" folder {path} created")


    def data_process(self, update=False, download=False, data_from="csv"):
        """Get the data

        Args:
            update (bool, optional): recreate the dataset. Defaults to False.
            data_from (str, optional): where does the data come from. Defaults to "csv".
        """

        logger.info("processing...")        
        if update:

            if download and data_from=="csv":
                self.data_download(
                    paths=[self.path_csv_power, self.path_csv_temp, self.path_csv_weather],
                    urls=[LINK_CSV_POWER, LINK_CSV_TEMP, LINK_CSV_WEATHER]
                )

            self.data_acquire(data_from=data_from)
            self.data_join()
            self.data_save()
        else:
            #Load data from db
            try:
                self.data_load()
                
                if self.df.empty:
                    raise Exception("the loaded database is empty")

            except Exception as exce:
                logger.error("unable to load the database. A new one will be created")
                self.data_process(update=True)

        logger.info(f"the data has been processed successfully")

    def data_save(self, ):
        """Save the dataset to a database
        """
        store.save_sql(self.df, self.path_db_expanded, sql_table="expanded", if_exists="replace")

    def data_load(self):
        """Load the dataset from a databace
        """
        self.df = store.load_sql(self.path_db_expanded, sql_table="expanded")

    def get_download_datetime(self):

        if self.path_csv_power.exists():
            timestamp = os.path.getmtime(self.path_csv_power)
        elif self.path_db_expanded.exists():
            timestamp = os.path.getmtime(self.path_csv_power)

        return datetime.fromtimestamp(timestamp)

    def data_download(self, paths=[], urls=[]):

        for path, url in zip(paths, urls):
            collector.from_web(url, path, DATASET_RAW_FOLDER)

    def data_acquire(self, data_from="csv"):
        """Get the data from csv files

        If the csv file is not present, it will be downloaded before reading.

        Args:
            data_from (str, optional): "csv" or "api". Defaults to "csv".
        """

        if data_from == "csv":

            # Read (and get) the temp csv file
            if not self.path_csv_temp.exists():
                self.data_download(paths=[self.path_csv_temp,], urls=[LINK_CSV_TEMP])
            df_temp_raw = collector.from_csv(self.path_csv_temp)

            # Read (and get) the weather csv file
            if not self.path_csv_weather.exists():
                self.data_download(paths=[self.path_csv_weather,], urls=[LINK_CSV_WEATHER])
            df_weather_raw = collector.from_csv(self.path_csv_weather)    

            # Read (and get) the power csv file
            if not self.path_csv_power.exists():
                self.data_download(paths=[self.path_csv_power,], urls=[LINK_CSV_POWER])
            df_power_raw = collector.from_csv(self.path_csv_power)

        elif data_from == "api":

            pass
            # select_power = "%2C".join(COL_POWER+["date", "heure", "consommation"])
            # where_power = "nucleaire%3E0"
            # limit_power=-1
            
            # url_power_json = f"https://odre.opendatasoft.com/api/v2/catalog/datasets/eco2mix-national-cons-def/exports/json?select={select_power}&where={where_power}&limit={limit_power}&offset=0&timezone=UTC"
            
            # df_power_raw = collector.from_api(url_power_json)
            
            # select_temp = "%2C".join(COL_TEMP + ["date",])
            # limit_temp=-1
            # df_temp_raw = collector.from_api(f"https://odre.opendatasoft.com/api/v2/catalog/datasets/temperature-quotidienne-regionale/exports/json?select={select_temp}&limit={limit_temp}&offset=0&timezone=UTC")
        
            # limit_weather=-1       
            # select_weather = "%2C".join(["date", "uv100", "ssrd03h"])
            # df_weather_raw = collector.from_api(f"https://odre.opendatasoft.com/api/v2/catalog/datasets/rayonnement-solaire-vitesse-vent-tri-horaires-regionaux/exports/json?select={select_weather}&limit={limit_weather}&offset=0&timezone=UTC")

        # Clean the raw datasets
        self.df_power = self.data_transform(df_power_raw, type_="power", data_from=data_from)
        self.df_temp = self.data_transform(df_temp_raw, type_="temp", data_from=data_from)  
        self.df_weather = self.data_transform(df_weather_raw, type_="weather", data_from=data_from)

    def data_transform(self, df, type_="temp", data_from="api"):

        if type_ == "temp":
            return cleaner.clean_temp(df, columns=COL_TEMP, data_from=data_from)

        elif type_ == "weather":           
            return cleaner.clean_weather(df, columns=COL_WEATHER, data_from=data_from)            

        elif type_ == "power":
            return cleaner.clean_power(df, columns=COL_POWER, data_from=data_from)

    def data_join(self, ):

        weather_index_hourly = pd.date_range(start=self.df_weather.index.min(), end=self.df_weather.index.max(), freq="1H")
        self.df_weather = self.df_weather.reindex(weather_index_hourly).interpolate(method="linear")

        power_index_hourly = pd.date_range(start=self.df_power.index.min(), end=self.df_power.index.max(), freq="1H")
        self.df_power = self.df_power.reindex(power_index_hourly).interpolate(method="linear")

        temp_index_hourly = pd.date_range(start=self.df_temp.index.min(), end=self.df_temp.index.max(), freq="1H")
        self.df_temp = self.df_temp.reindex(temp_index_hourly).interpolate(method="linear")

        df_power_weather = self.df_power.join(self.df_weather)
        self.df = df_power_weather.join(self.df_temp)

        cleaner.clean_nan_rows(self.df)

        self.df.index.name = "longdate"

    def train_model(self, model):
        """Launch the training of a model

        Args:
            model (ModelProphet): instance

        Returns:
            bool: True if correctly trained, False if error
        """

        try:

            # Get the training data
            df_train = self.data_serve(end=model.end_training, columns=model.columns_base)

            # Build the model and train it
            model.train(df_train)

            return True

        except Exception as exce:
            logger.error(f"unable to train {model.name} : {exce}")
            return False


    def build_models(self):
        """Build ModelProphet instances with the parameters given by self.models
        """


        for name, parameters in self.models.items():

            # Get the parameters of the model
            target = parameters.get("target")
            regressors = parameters.get("regressors")
            end_training = parameters.get("end_training")
            columns = [target, ]+regressors

            # Creation
            model = models.ModelProphet(
                name=name, 
                target_column=target, 
                regressor_columns=regressors,
                end_training=end_training)          

            # Model stored in the dict
            parameters["model"] = model

            logger.info(f"model {name} is initialized")

    def train_models(self):
        """Launch the training of all models
        """

        for parameters in self.models.values():
            # Get the model
            model = parameters.get("model")
            
            # Train it
            trained = self.train_model(model)

            # Store if it has been trained or not
            parameters["trained"] = trained

            logger.info(f"model {model.name} is trained")
            

    def data_serve(self, start=None, end=None, date=None, columns=[], only_index=False):
        """Send a part of the dataframe based on the selection variables

        Args:
            start (_type_, optional): _description_. Defaults to None.
            end (_type_, optional): _description_. Defaults to None.
            date (_type_, optional): _description_. Defaults to None.
            columns (list, optional): _description_. Defaults to [].

        Returns:
            pd.Dataframe: _description_
        """

        if only_index:
            
            return self.df.index

        else:
            
            df_dates = selector.get_dates(self.df, start=start, end=end, date=date )
            df_columns = selector.get_columns(df_dates, columns=columns)

            text = f"dates bewteen {start} and {end}" if not date else f"date equal to {date}"
            logger.debug(f"df restricted to {text}")
            logger.debug(f"columns selected for df : {columns}")

            return df_columns
    
    def data_test(self, start=None, end=None, extra_columns=[],  model_name=None):
        """_summary_

        Args:
            start (_type_, optional): _description_. Defaults to None.
            end (_type_, optional): _description_. Defaults to None.
            extra_columns (list, optional): _description_. Defaults to [].
            model_name (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
       
        # Get the model
        model = self.models.get(model_name).get("model")
        
        # If it is not trained
        if not model.trained:
            logger.warning(f"{model_name} is not trained. Trying to load it from a pkl file")

            try:
                # Try to load it from it's pkl file
                model.load()

            except Exception as exce:
                logger.warning(f"{model_name} couldn't be loaded. Train it !")
                # If the model couldn't be loaded, train or retrain it
                self.train_model(model)

        else:
            logger.info(f"{model_name} is loaded and trained")

        columns = model.columns_base + extra_columns

        # Get the test data
        df_test = self.data_serve(start=start, end=end, columns=columns, only_index=False)

        # Make a prediction
        forecast = model.test(df_test)

        # Return prediction and model
        return forecast, model

if __name__ == "__main__":

    
    parser = argparse.ArgumentParser(description='Provide options for the pipeline.')

    parser.add_argument('-u', "--update", 
                    action='store_true',
                    help='update the dataset with the csv files')

    parser.add_argument('-d', "--download", 
                    action='store_true',
                    help='download the datasets from the web')

    parser.add_argument('-sd', "--start-date",            
                    type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M'),
                    help='date in the YYYY-mm-ddTHH:MM format ')

    parser.add_argument('-n', "--next-days",            
                    type=int,
                    default=21,
                    help='number of days to predict after start-date')

    parser.add_argument('-m', "--model_name",            
                    type=str,
                    default="prophet_time",
                    help='name of the model used in ("prophet_time", "prophet_temp", "prophet_weather")')       

    parser.add_argument('-t', "--train-models",            
                    action='store_true',
                    help='train the models after pipeline creation')       

    args = parser.parse_args()

   # Build the pipeline
    pip = Pipeline()
    pip.data_process(update=args.update, download=args.download, data_from="csv")
    pip.build_models()

    # Train the models if asked
    if args.train_models:

        pip.train_models()

    # If a date is given, make a prediction
    if args.start_date:

        start = args.start_date + timedelta(hours=0) + timedelta(minutes=0)
        end = start + timedelta(days=args.next_days)

        # Get the test data according to the given dates
        forecast, model = pip.data_test(start=start, end=end, extra_columns=["prevision_j1", ],  model_name=args.model_name)

        # Plot the forecast and its components
        fig_forecast = model.fbmodel.plot(forecast)
        fig_components = model.fbmodel.plot_components(forecast)

        plt.show()