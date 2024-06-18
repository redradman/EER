import pandas as pd

# variable that can be changed (ensure that the header match the sample)
CSV_file = "sample_data_multiple_links.csv"

# create df 
df = pd.read_csv(CSV_file, index_col = 0)


# convert the df to dictionary
df_dict = df.to_dict()

# checkpoint: YES
# print(df_dict)


# print(list(df_dict.keys())[0])


maindict = df_dict[list(df_dict.keys())[0]]
print(maindict)