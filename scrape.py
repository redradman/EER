###############################
##################### libraries

from tqdm import tqdm
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv

###############################
##################### variables
# csv file that can be changed (ensure that the header match the sample)
CSV_file = "data/sample_data.csv"
XLSX_FILE = "data/sample_data.xlsx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

###############################
##################### functions 

# read functions 
def read_file(file):
    """ 
    determine which reader to use based on the suffix and read the given file
    """
    if file.split(".")[-1] == "csv":
        print(f"reading {file}")
        df = pd.read_csv(file, index_col = 0)
    if file.split(".")[-1] == "xlsx":
        print(f"reading {file}")
        df = pd.read_excel(file, index_col = 0)
    return df

# extract links
def link_extractor(file =  XLSX_FILE):
    """
    gets the csvfile and returns the dataframe, generated dictionary with programs as key and the list of links as the corressponding entry
    """
    df = read_file(file)
        

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
            no_space_list = [link.replace("\n","") for link in no_space_list]
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
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200: 
            print(f"Could not access {url}, error code: {response.status_code}")
            # raise ValueError('Status code not 200. Connection cannot be established correctly')
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
    
    
# save programs data
def save_scraped_programs_csv(database_to_save, file_name = "data/scraping_results.csv"):
    """ 
    get the dictionary containing the programs and save as csv with the intended name
    """
    csv_data = [] 
    header = ["program", "link", "text"]
    csv_data.append(header)
    # csv_file_path = 'results.csv'
    for program in database_to_save:
        for link_text_pair in database_to_save[program]:
            keys = link_text_pair.keys()
            for key in keys:
                data = [program, # name of program 
                        key, # link 
                        link_text_pair[key]] # extracted text
                csv_data.append(data)

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

df, dict_with_links = link_extractor()

def programs_maker(): 
# generated database used to store the extracted text with the tags
    programs = {}
    # extract the text from the links 
    for program in tqdm(dict_with_links.keys(), desc="Programs"):  # access the list containing the links for each of the programs
        for link in tqdm(dict_with_links[program], desc=f"Processing {program}", leave=False):  # access each of the links in the list 
            text = get_plaintext_from_url(link) # extract text
            clean_text = clean_extracted_text(text) # clean text of spaces and unnecessary details 
            add_program(programs, program, link, clean_text) # add the result to the database dictionary
    return programs

###############################
##################### main

if __name__ == "__main__":
    programs = programs_maker()
    save_scraped_programs_csv(programs)


##### SCRAPING IS FINISHED

