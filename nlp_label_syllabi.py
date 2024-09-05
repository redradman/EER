############################# importing the libraries
#####################################################
# used for processing the data
import torch
from transformers import pipeline
import pandas as pd

# used for handling the stop words and unnecessary segments
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import ssl

import logging # logging the data in a file instead of traditional print statements
from openpyxl import load_workbook # used for written to excel file without overwriting other sheets

from nlp_label_funcs import *

############################################## set up
#####################################################

# set up logging
logging.basicConfig(
    filename='nlp_label_syllabi_log.txt', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("#####################################################")
logging.info("#####################################################")
logging.info("setting up")

DATA = "data/EER_CourseSyllabi_cleaned.csv"
data = pd.read_csv(DATA)

print(data.head())