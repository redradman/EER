import spacy
import pandas as pd


DATA = "scraping_results.csv"
COMPETENCIES = "cocurricular_competencies.xlsx"

nlp = spacy.load("en_core_web_md")

df = pd.read_excel(COMPETENCIES)
data_df = pd.read_csv(DATA)

# read the words associated with the skill

# for i in range(df.shape[0]):
    
#     # print(f"{df.at[i, 'Comptency']}: {df.at[i, 'keyword']}")
    
#     keywords = df.at[i, 'keyword']
#     keywords = keywords.split(", ")
#     print(keywords)
#     pass

keywords = df.at[0, 'keyword']



