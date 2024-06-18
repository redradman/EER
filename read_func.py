import pandas as pd

# variable that can be changed (ensure that the header match the sample)
CSV_file = "sample_data_multiple_links.csv"

# create df 
df = pd.read_csv(CSV_file, index_col = 0)


# convert the df to dictionary
df_dict = df.to_dict()

maindict = df_dict[list(df_dict.keys())[0]]

for key in maindict.keys():
    link_string = maindict[key]
    # check if there is an entry 
    if isinstance(link_string, str):
        # generate a list and seperate the links using | as a delim 
        parsed_list = link_string.split('|')
        # removal of any whitespaces from all links
        no_space_list = list(map(lambda x: x.replace(" ", ""), parsed_list))
        # print(parsed_list)
        # CHECKPOINT: YES
        print(no_space_list)