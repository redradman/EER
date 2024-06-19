###############################
##################### libraries

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

###############################
##################### variables
# csv file that can be changed (ensure that the header match the sample)
CSV_file = "sample_data.csv"

###############################
##################### functions 

# read functions 

def link_extractor(csvfile =  CSV_file):
    """
    gets the csvfile and returns the dataframe, generated dictionary with programs as key and the list of links as the corressponding entry
    """
    df = pd.read_csv(csvfile, index_col = 0)

    # convert the df to dictionary
    df_dict = df.to_dict()

    maindict = df_dict[list(df_dict.keys())[0]]

    dict_with_extracted_links = {}

    for key in maindict.keys():
        link_string = maindict[key]
        # check if there is an entry 
        if isinstance(link_string, str):
            # generate a list and seperate the links using | as a delim 
            parsed_list = link_string.split('|')
            # removal of any whitespaces from all links
            no_space_list = list(map(lambda x: x.replace(" ", ""), parsed_list))
            # print(no_space_list)
            dict_with_extracted_links[key] = no_space_list
            # print(dict_with_extracted_links)
        
    return df, dict_with_extracted_links


# establishing a connection
def get_plaintext_from_url(url):
    """ 
    establish a connection with the url and extract the text and return it
    """
    try:
        # Send a GET request
        response = requests.get(url)
        if response.status_code != 200: 
            raise ValueError('Status code not 200. Connection cannot be established correctly')
        response.raise_for_status() # halt if unsuccessful, throws an error
        # Parse HTML via BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract plain text
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    
# regex cleaning
def clean_extracted_text(text: str):
    """ 
    clean text using regex
    """
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    cleaned_text = re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', ' ', cleaned_text)
    cleaned_text = re.sub(r'\n\s+', '\n', cleaned_text).strip()
    return cleaned_text
    
# program adder
def add_program(dict_to_add_to, program_name, link, text):
    """ 
    add a program to dictionary with its link and text as elements in the list (entry) associated with the program (key)
    """
    if program_name not in dict_to_add_to:
        dict_to_add_to[program_name] = []
    dict_to_add_to[program_name].append({link: text})