# Libraries
from fbprophet import Prophet
from sklearn.model_selection import train_test_split
from fbprophet.plot import plot_components_plotly
import logging

# Modules
import store

# Constants
from config import MODELS_FOLDER

logger = logging.getLogger("journal")

class ModelProphet():
    def __init__(self, *args, **kwargs):

        self.target = kwargs.get("target_column")
        self.regressors = kwargs.get("regressor_columns")
        self.name = kwargs.get("name")
        self.end_training = kwargs.get("end_training")
        
        self.columns_base = [self.target, ] + self.regressors
        self.folder = MODELS_FOLDER
        self.trained = False
        self.fbmodel = None

    def prepare_df_for_prophet(self, df):
        """Reorganize the columns of the df for fbprophet.

        * column 'ds' for the time-series
        * column 'y' for the target
        * other columns for the regressors

        Args:
            df (pd.DataFrame): dataframe

        Returns:
            pd.DataFrame: reorganized dataframe
        """

        # Reset the index so that the longdate will now be a column
        df = df.reset_index()

        # Rename the columns. Prophet works with 'ds' and 'y' columns
        df = df.rename(columns={
            "longdate" : "ds",
            self.target : "y",
            })

        # Required columns are 'ds', 'y' and all the regressors
        columns = self.regressors + ["ds", "y"]

        # Selected the required columns
        df = df.loc[:, columns]

        logger.debug(f"df is prepared for training or testing")

        return df

    def train(self, df_train, growth='flat', autosave=True):
        """Train the model based on the training data

        Args:
            df_train (pd.DataFrame): dataframe containing the training data
            growth (str, optional): _description_. Defaults to 'flat'.
            autosave (bool, optional): save the model after the fitting process. Defaults to True.
        """

        # Prepare the training data
        df_train = self.prepare_df_for_prophet(df_train)

        # Create the model with seasonalities
        fbmodel = Prophet(
            growth=growth,
            #changepoint_prior_scale=0.001,
            yearly_seasonality = True,
            weekly_seasonality = True,
            daily_seasonality = True
        )

        # Add regressors to the model if necessary
        for regressor in self.regressors:
                fbmodel.add_regressor(regressor)

        # Fit the model
        fbmodel.fit(df_train)

        # Keep the model 
        self.fbmodel = fbmodel
        self.df_train = df_train

        self.trained = True

        # Save it if necessary
        if autosave:
            self.save(self.fbmodel, self.name, self.folder)

        logger.info(f"{self.name} is trained")

    def test(self, df_test):
        
        # Prepare the testing data
        self.df_test = self.prepare_df_for_prophet(df_test)

        # Return the predicted data
        forecast = self.fbmodel.predict(self.df_test)

        logger.info(f"forecast prediction done by {self.name}")
        return forecast

    def save(self, fbmodel, name, folder):
        
        store.save_model(fbmodel, name=name, folder=folder)
        
        logger.info(f"{self.name} is saved")

    def load(self, ):

        self.fbmodel = store.load_model(self.name, self.folder)
        self.trained = True

        logger.info(f"{self.name} is loaded from its pkl file")

    def get_plotly_components(self, forecast, skip_trend=True):
        
        # Get the components (yearly, hourly, etc...) 
        components = plot_components_plotly(self.fbmodel, forecast)

        # If skip_trend, we remove the trend component
        if skip_trend:
            components._data = components._data[1:]

        # Return the components
        return components