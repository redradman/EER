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

from nlp_label_funcs import aggregate_scraped_texts
from nlp_label_funcs import make_competency_and_keywords_dictionary
from nlp_label_funcs import classify_text
from nlp_label_funcs import save_raw_data_as_csv
from nlp_label_funcs import generate_column_values
from nlp_label_funcs import save_data_to_excel

############################################## set up
#####################################################
# set up logging
logging.basicConfig(
    filename='nlp_label_log.txt', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("#####################################################")
logging.info("#####################################################")
logging.info("setting up")

DATA = "data/clean_data.csv"
COMPETENCIES = "data/cocurricular_competencies.xlsx"
PROGRAM_LIST = ['e@UBCV', 'e@UBCO', 'UBC Social Enterprise Club', 'eProjects UBC', 'Enactus UBC', 'Innovation UBC Hub', 'Summit Leaders', 'UBC Sauder LIFT', 'UBC MBA Innovation & Entrepreneurship club', 'Innovation on Board', 'Engineers without borders', 'Startup Pitch Competition event: UBC SOAR']

coc = pd.read_excel(COMPETENCIES)
data = pd.read_csv(DATA)
# deal with the ssl certificate for nltk download
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('stopwords')
nltk.download('punkt')


# Initialize the zero-shot classifier from facebook via HF
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")

############################# running the classification on bart
###############################################################
logging.info("Running body of the code")

logging.info("Creating aggregate from scraped texts")
text_hashmap = aggregate_scraped_texts(data, "program")

logging.info("Creating hashmap of competency and keywords")
competency_and_keywords_hashmap = make_competency_and_keywords_dictionary(coc)

logging.info("Commence classification")
program_scores = classify_text(text_hashmap, competency_and_keywords_hashmap)

logging.info("Saving raw data as csv file")
save_raw_data_as_csv(program_scores, 'data/program_scores_raw.csv')

# logging.info("Including scores in log file")
# include_scores_in_log_file(program_scores)

logging.info("Converting numeric model value to binary classifcation")
generate_column_values(coc, PROGRAM_LIST, program_scores)
    
logging.info("Saving data as excel")
save_data_to_excel(coc, COMPETENCIES)


logging.info("Code Executed Successfully")
logging.info("#####################################################")