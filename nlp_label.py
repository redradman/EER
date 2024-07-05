import spacy
import pandas as pd


DATA = "clean_data.csv"
COMPETENCIES = "cocurricular_competencies.xlsx"

nlp = spacy.load("en_core_web_md")

coc = pd.read_excel(COMPETENCIES)
data = pd.read_csv(DATA)


# read the words associated with the skill

# for i in range(df.shape[0]):
    
#     # print(f"{df.at[i, 'Comptency']}: {df.at[i, 'keyword']}")
    
#     keywords = df.at[i, 'keyword']
#     keywords = keywords.split(", ")
#     print(keywords)
#     pass

keywords = coc.at[0, 'keyword']
print(keywords)

# append all of the string for each program to each other 
# after this the number of rows/keys in the dict is the program and the value for that key is all of the text associated with that program
text_hashmap = dict.fromkeys(data["program"], '')
for row in data.values:
    if type(row[2]) == str:
        text_hashmap[row[0]] += row[2]



