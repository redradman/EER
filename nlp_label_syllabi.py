############################# importing the libraries
#####################################################
from transformers import pipeline
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

############################################## constants
#####################################################
THRESHOLD = 0.5
DATA = "data/EER_CourseSyllabi_cleaned.csv"
COMPETENCIES = "data/cocurricular_competencies.xlsx"
COLUMNS_TO_AGGREGATE = [
    "Learning Objectives",
    "Course Description and Topics",
    "Assignment Descriptions"
]

def preprocess_syllabi_text(text):
    """
    Preprocess syllabi text by removing stopwords and non-alphabetic tokens
    """
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = " ".join([word for word in word_tokens if word.isalpha() and word not in stop_words])
    return filtered_text

def combine_syllabi_text_columns(data, columns_to_combine):
    """
    Combines specified columns for each course into a single text
    """
    text_hashmap = {}
    for _, row in data.iterrows():
        course_code = row["Course code"]
        combined_text = ""
        for column in columns_to_combine:
            if column in data.columns and pd.notna(row[column]):
                combined_text += str(row[column]) + " "
        if combined_text.strip():
            text_hashmap[course_code] = combined_text.strip()
    return text_hashmap

def create_competency_keywords_map(competencies_df):
    """
    Creates mapping between competencies and their keywords
    """
    comp_keywords = {}
    competencies = competencies_df["Comptency"].to_list()
    for comp in competencies:
        keywords = competencies_df[competencies_df["Comptency"] == comp]["keyword"].to_list()
        comp_keywords[comp] = keywords
    return comp_keywords

def classify_syllabi_text(text_hashmap, comp_keywords_map, chunk_size=512):
    """
    Classifies syllabi text against competencies and keywords
    """
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="auto")
    all_results = {}

    for course_code, text in text_hashmap.items():
        logging.info(f"Processing course: {course_code}")
        processed_text = preprocess_syllabi_text(text)
        chunks = [processed_text[i:i + chunk_size] for i in range(0, len(processed_text), chunk_size)]
        
        course_results = {}
        for competency, keywords in comp_keywords_map.items():
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
            
            course_results[competency] = {
                'competency_score': final_comp_score,
                'keyword_score': final_keyword_score,
                'total_score': final_total_score
            }
        
        all_results[course_code] = course_results
    
    return all_results

def save_syllabi_results(results, output_file):
    """
    Saves syllabi classification results to CSV
    """
    rows = []
    for course, competencies in results.items():
        for competency, scores in competencies.items():
            rows.append({
                'course_code': course,
                'competency': competency,
                'competency_score': scores['competency_score'],
                'keyword_score': scores['keyword_score'],
                'total_score': scores['total_score']
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)
    logging.info(f"Results saved to {output_file}")

############################################## main execution
#####################################################
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        filename='nlp_label_syllabi_log.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("Starting syllabi analysis")
    
    # Load data
    syllabi_data = pd.read_csv(DATA)
    competencies_data = pd.read_excel(COMPETENCIES)
    
    # Process syllabi
    text_hashmap = combine_syllabi_text_columns(syllabi_data, COLUMNS_TO_AGGREGATE)
    comp_keywords_map = create_competency_keywords_map(competencies_data)
    
    # Run classification
    results = classify_syllabi_text(text_hashmap, comp_keywords_map)
    
    # Save results
    save_syllabi_results(results, 'data/syllabi_scores.csv')
    
    logging.info("Syllabi analysis completed")