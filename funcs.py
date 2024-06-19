###############################
##################### libraries

import pandas as pd

###############################
##################### variables
# csv file that can be changed (ensure that the header match the sample)
CSV_file = "sample_data_multiple_links.csv"



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



    