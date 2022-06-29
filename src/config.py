# Columns of interest in multiple datasets
COL_POWER = ["consommation", "prevision_j1", "fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "pompage", "bioenergies"]
COL_TEMP = ["tmin", "tmax", "tmoy"]
COL_WEATHER = ["wspd", "sun"]
COL_VISUALISATION_PRODUCTION = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "pompage", "bioenergies"]

# Logging
LOGS_FOLDER = "./logs/"
LOG_LEVEL = "INFO"

# Folders
MODELS_FOLDER = "./models/"
DATASET_RAW_FOLDER = "./datasets/raw"
DATASET_PROCESSED_FOLDER = "./datasets/processed"

# Database
NAME_DB_EXPANDED = "db_expanded.db"

# Csv files
NAME_CSV_POWER = "eco2mix-national-cons-def.csv"
NAME_CSV_TEMP = "temperature-quotidienne-regionale.csv"
NAME_CSV_WEATHER = "rayonnement-solaire-vitesse-vent-tri-horaires-regionaux.csv"

# Links and urls
LINK_CSV_POWER = "https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
LINK_CSV_TEMP = "https://odre.opendatasoft.com/explore/dataset/temperature-quotidienne-regionale/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
LINK_CSV_WEATHER = "https://odre.opendatasoft.com/explore/dataset/rayonnement-solaire-vitesse-vent-tri-horaires-regionaux/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"

