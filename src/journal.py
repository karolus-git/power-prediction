# Libraries
import logging
import colorlog
import warnings
from logging import FileHandler
from logging import Formatter
from colorlog import ColoredFormatter
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Constants
from config import LOGS_FOLDER, LOG_LEVEL


def init_journal(avoid_matplotlib=True, ignore_future=True):
	"""Initialization of the logger

	Args:
		avoid_matplotlib (bool, optional): push matplotlib logs to WARNING. Defaults to True.

	Returns:
		logging.logger: logger
	"""

	# Load a basic config with a given log level
	logging.basicConfig(level=LOG_LEVEL)
	
	if avoid_matplotlib:
		# Set matplotlib to an other level
		logging.getLogger('matplotlib').setLevel(logging.WARNING)

	if ignore_future:
		# Ignore the future warnings
		warnings.simplefilter(action='ignore', category=FutureWarning)

	# Color formatter for the stream
	stream_formatter = ColoredFormatter(
		"%(asctime)s %(log_color)s %(module)-8s %(levelname)-8s%(reset)s %(blue)s%(message)s",
		datefmt=None,
		reset=True,
		log_colors={
			'DEBUG':    'cyan',
			'INFO':     'green',
			'WARNING':  'yellow',
			'ERROR':    'red',
			'CRITICAL': 'red,bg_white',
		},
		secondary_log_colors={},
		style='%'
	)

	# Basic rortating formatter for the file
	file_formatter = Formatter(
		'%(asctime)s %(module)-8s %(levelname)-8s%(message)s'
	)

	# The stream handler
	stream_handler = colorlog.StreamHandler()
	file_handler = RotatingFileHandler(Path(LOGS_FOLDER, "journal.log"), maxBytes=1000*512, backupCount=10)

	# The file handler
	stream_handler.setFormatter(stream_formatter)
	file_handler.setFormatter(file_formatter)

	# The logger will be called "journal"
	logger = logging.getLogger("journal")
	
	# The handlers are added to the logger
	logger.addHandler(stream_handler)
	logger.addHandler(file_handler)

	# Trick to avoid duplicate stream messages, but should'nt be necessary
	logger.propagate=False

	return logger
