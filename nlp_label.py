############################# importing the libraries
#####################################################
from transformers import pipeline
import pandas as pd
import nltk
import ssl
import logging

# Import helper functions
from nlp_label_funcs import (
    preprocess_text,
    aggregate_scraped_texts,
    make_competency_and_keywords_dictionary,
    save_raw_data_as_csv,
    generate_column_values,
    save_data_to_excel
)

############################################## constants
#####################################################
THRESHOLD = 0.5
DATA = "data/clean_data.csv"
COMPETENCIES = "data/cocurricular_competencies.xlsx"
PROGRAM_LIST = ['e@UBCV', 'e@UBCO', 'UBC Social Enterprise Club', 'eProjects UBC', 
                'Enactus UBC', 'Innovation UBC Hub', 'Summit Leaders', 'UBC Sauder LIFT', 
                'UBC MBA Innovation & Entrepreneurship club', 'Innovation on Board', 
                'Engineers without borders', 'Startup Pitch Competition event: UBC SOAR']

def classify_text(text_hashmap, competency_and_keywords_hashmap, chunk_size=512):
    """
    Classifies program text against competencies and keywords
    """
    # Initialize classifier inside the function for reproducibility
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")
    all_results = {}

    for program, text in text_hashmap.items():
        logging.info(f"Processing program: {program}")
        processed_text = preprocess_text(text)
        chunks = [processed_text[i:i + chunk_size] for i in range(0, len(processed_text), chunk_size)]
        
        program_results = {}
        for competency, keywords in competency_and_keywords_hashmap.items():
            comp_scores = []
            keyword_scores = []
            
            for chunk in chunks:
                # Competency classification
                comp_result = classifier(chunk, candidate_labels=[competency])
                comp_scores.append(comp_result['scores'][0])
                
                # Keywords classification
                chunk_keyword_scores = []
                for keyword in keywords:
                    keyword_result = classifier(chunk, candidate_labels=[keyword])
                    chunk_keyword_scores.append(keyword_result['scores'][0])
                keyword_scores.append(sum(chunk_keyword_scores) / len(chunk_keyword_scores))
            
            # Calculate final scores
            final_comp_score = sum(comp_scores) / len(comp_scores)
            final_keyword_score = sum(keyword_scores) / len(keyword_scores)
            final_total_score = (final_comp_score + final_keyword_score) / 2
            
            program_results[competency] = {
                'average_competency_score': final_comp_score,
                'average_keyword_score': final_keyword_score,
                'average_total_aggregate_score': final_total_score
            }
        
        all_results[program] = program_results
    
    return all_results

############################################## main execution
#####################################################
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        filename='nlp_label_log.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("Starting program analysis")
    
    # SSL certificate handling for NLTK
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    nltk.download('stopwords')
    nltk.download('punkt')
    
    # Load data
    data = pd.read_csv(DATA)
    coc = pd.read_excel(COMPETENCIES)
    
    # Create text and competency hashmaps
    logging.info("Creating aggregate from scraped texts")
    text_hashmap = aggregate_scraped_texts(data, "program")
    
    logging.info("Creating hashmap of competency and keywords")
    competency_and_keywords_hashmap = make_competency_and_keywords_dictionary(coc)
    
    # Run classification
    logging.info("Commence classification")
    program_scores = classify_text(text_hashmap, competency_and_keywords_hashmap)
    
    # Save results
    logging.info("Saving raw data as csv file")
    save_raw_data_as_csv(program_scores, 'data/program_scores_raw.csv')
    
    logging.info("Converting numeric model value to binary classification")
    generate_column_values(coc, PROGRAM_LIST, program_scores)
    
    logging.info("Saving data as excel")
    save_data_to_excel(coc, COMPETENCIES)
    
    logging.info("Code Executed Successfully")