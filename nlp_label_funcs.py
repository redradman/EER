############################# importing the libraries
#####################################################
# used for processing the data
from transformers import pipeline
import pandas as pd

# used for handling the stop words and unnecessary segments
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import logging # logging the data in a file instead of traditional print statements
from openpyxl import load_workbook # used for written to excel file without overwriting other sheets

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")

##################################################### functions
###############################################################

def preprocess_text(text):
    """
    preprocess text by reomving the stop words
    """
    logging.info("Preprocessing text...")
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)

    # Remove stop words and non-alphabetic tokens to prevent tampering with scoring
    filtered_text = " ".join([word for word in word_tokens if word.isalpha() and word not in stop_words])
    logging.info("Text preprocessing completed.")
    return filtered_text

###############################################################

def aggregate_scraped_texts(data, program_name: str):
    """ 
    combines the extracted texts from scraping together
    """
    text_hashmap = dict.fromkeys(data[program_name], '')
    for row in data.values:
        if isinstance(row[2], str):
            text_hashmap[row[0]] += row[2]
    return text_hashmap

###############################################################

def make_competency_and_keywords_dictionary(coc):
    """
    get the list of keywords associated with the competency and create a key value pair with a hashmap for them and return it
    """
    comptencies_and_keywords_dict = {}
    comptencies = coc["Comptency"].to_list()
    for comp in comptencies:
        keywords = coc[coc["Comptency"] == comp]["keyword"].to_list()
        comptencies_and_keywords_dict[comp] = keywords
    return comptencies_and_keywords_dict

###############################################################

def classify_text(text_hashmap, competency_and_keywords_hashmap, chunk_size=512):
    all_results = {}

    # Iterate over each program in the hashmap
    for program_name, text in text_hashmap.items():
        logging.info(f"Processing program: {program_name}")

        # Preprocess the text for each program
        processed_text = preprocess_text(text)

        # Break text into chunks of `chunk_size`
        chunks = [processed_text[i:i + chunk_size] for i in range(0, len(processed_text), chunk_size)]
        results_per_chunk = []

        logging.info(f"Total chunks to process for {program_name}: {len(chunks)}")

        # Classify each chunk
        for i, chunk in enumerate(chunks, start=1):
            logging.info(f"Classifying chunk {i}/{len(chunks)} for program: {program_name}")

            # Initialize results for this chunk
            chunk_results = {}

            # Process each competency and its keywords
            for competency, keywords in competency_and_keywords_hashmap.items():
                logging.info(f"Evaluating competency: {competency} for program: {program_name}")

                # Classify the competency
                competency_result = classifier(chunk, candidate_labels=competency)
                competency_score = competency_result['scores'][0]

                # Classify the keywords
                keyword_scores = []
                for keyword in keywords:
                    keyword_result = classifier(chunk, candidate_labels=[keyword])
                    keyword_scores.append(keyword_result['scores'][0])

                # Calculate aggregate keyword score
                aggregate_keyword_score = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0

                # Calculate total aggregate score
                total_aggregate_score = (competency_score + aggregate_keyword_score) / 2

                # Store results
                chunk_results[competency] = {
                    'competency_score': competency_score,
                    'aggregate_keyword_score': aggregate_keyword_score,
                    'total_aggregate_score': total_aggregate_score,
                    'keyword_scores': keyword_scores
                }

            results_per_chunk.append(chunk_results)
            logging.info(f"Chunk {i} classification completed for program: {program_name}")

        # Aggregate results for this program
        all_results[program_name] = aggregate_results(results_per_chunk, competency_and_keywords_hashmap)

    return all_results


###############################################################

def aggregate_results(results, competency_and_keywords_hashmap):
    logging.info("Aggregating results across all chunks...")
    aggregated_scores = {}

    for competency in competency_and_keywords_hashmap:
        competency_scores = []
        keyword_scores = []

        for result in results:
            if competency in result:
                competency_scores.append(result[competency]['competency_score'])
                keyword_scores.append(result[competency]['aggregate_keyword_score'])

        # Calculate average scores
        avg_competency_score = sum(competency_scores) / len(competency_scores) if competency_scores else 0
        avg_keyword_score = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0
        avg_total_aggregate_score = (avg_competency_score + avg_keyword_score) / 2

        # Store aggregated scores
        aggregated_scores[competency] = {
            'average_competency_score': avg_competency_score,
            'average_keyword_score': avg_keyword_score,
            'average_total_aggregate_score': avg_total_aggregate_score
        }

    logging.info("Aggregation completed.")
    return aggregated_scores

### Display and log the final scores for each program
#####################################################
def include_scores_in_log_file(scores):
    for program_name, scores in scores.items():
        # print(f"\nProgram: {program_name}")
        logging.info(f"\nProgram: {program_name}")
        
        for competency, score_details in scores.items():
            competency_score = score_details['average_competency_score']
            keyword_score = score_details['average_keyword_score']
            total_aggregate_score = score_details['average_total_aggregate_score']

            # print(f"  Competency: {competency}")
            # print(f"    Average Competency Score: {competency_score:.4f}")
            # print(f"    Average Keyword Score: {keyword_score:.4f}")
            # print(f"    Average Total Aggregate Score: {total_aggregate_score:.4f}")
            
            logging.info(f"  Competency: {competency}")
            logging.info(f"    Average Competency Score: {competency_score:.4f}")
            logging.info(f"    Average Keyword Score: {keyword_score:.4f}")
            logging.info(f"    Average Total Aggregate Score: {total_aggregate_score:.4f}")

        logging.info("Final scores calculated.")



######################## conversion of data to columns
#####################################################
def assign_binary_classification_value(program, competency, program_scores):
    """
    returns true if either of the:
        1. average_competency_score
        2. average_keyword_score
        3. average_total_aggregate_score
    are above > 0.5 threshold and otherwise false
    """
    return sorted(list(program_scores[program][competency].values()), reverse = True)[0] > 0.5

#####################################################
def fetch_column_values(program, program_scores):
    """
    converts the generated scores from the classfication model of BART to a column of binary (0 or 1) values 
    to be assigned to a program based on the competency score levels
    """
    column_values = []
    competencyScoresForProgram = program_scores[program]
    for competency in competencyScoresForProgram:
        column_values.append(assign_binary_classification_value(program, competency, program_scores))
    return column_values

############ generate the column values and save them
#####################################################
def generate_column_values(df, PROGRAM_LIST, program_scores): 
    for program in PROGRAM_LIST:
        logging.info("Generating the list containing the binary classification data for {program}")
        df[program] = fetch_column_values(program, program_scores)

########################## save program scores as csv
#####################################################
def save_raw_data_as_csv(results, path_to_file):
    data = []
    for program, skills in results.items():
        for skill, scores in skills.items():
            row = {
                'program': program,
                'skill': skill,
                'competency_score': scores['average_competency_score'],
                'keyword_score': scores['average_keyword_score'],
                'aggregate_score': scores['average_total_aggregate_score']
            }
            data.append(row)
    df = pd.DataFrame(data)
    df.to_csv(path_to_file, index=False)

####################################### save the data
#####################################################
def save_data_to_excel(df, path, name_of_sheet = "Sheet3"):
    book = load_workbook(path)

    # Create a Pandas Excel writer using openpyxl as the engine
    with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Write the DataFrame 'coc' to a specific sheet, 'Sheet3' in this case
        df.to_excel(writer, index=False, sheet_name='Sheet3')
    book.save(path) 