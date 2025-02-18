import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

def extract_course_number(course_code):
    """
    Extracts the numerical part of a course code for sorting.
    Example: 'COMM 386L' -> 386, 'BAEN 550A' -> 550
    """
    match = re.search(r'(\d+)', course_code)
    return int(match.group(1)) if match else 0

def load_and_prepare_data(syllabi_file, program_file):
    """
    Load and prepare both CSV files for visualization
    """
    # Load the data
    syllabi_df = pd.read_csv(syllabi_file)
    program_df = pd.read_csv(program_file)
    
    # Create modified syllabi dataframe with updated course codes
    syllabi_df_modified = syllabi_df.copy()
    code_mapping = {
        'COMM 280 (102-103/201-202)': 'COMM 280A',
        'COMM 280 (101 + 203)': 'COMM 280B',
        'COMM 382/COMR 382': 'COMM 382',
        'COMM 383, prev 386D': 'COMM 383',
        'COMM 387/COMR 387/COEC 387': 'COMM 387',
        'COMM/COMR 388': 'COMM 388',
        'COMM 466/APSC486/APSC496A/E  = 2 Term Course': 'COMM 466',
        'COMM 482 / BAMA 503 001': 'COMM 482',
        'COMM 486G / BAEN 510': 'COMM 486G',
        'COMM 497/  COMR 497': 'COMM 497',
        'BAEN 506/APSC 541': 'BAEN 506',
        'BAEN 549 (Angele)': 'BAEN 549',
        'BAEN 550 (Angele) - ': 'BAEN550A',
        'BAEN 550/FCOR 502 (Fraser Pogue)': 'BAEN550B',
        'ENPH 459 & 479': 'ENPH 459'
    }
    syllabi_df_modified['course_code'] = syllabi_df_modified['course_code'].replace(code_mapping)
    
    # Pivot the dataframes
    program_pivot = program_df.pivot(
        index='program',
        columns='skill',
        values='keyword_score'
    )
    
    syllabi_pivot = syllabi_df.pivot(
        index='course_code',
        columns='competency',
        values='keyword_score'
    )
    
    syllabi_pivot_modified = syllabi_df_modified.pivot(
        index='course_code',
        columns='competency',
        values='keyword_score'
    )
    
    # Sort syllabi pivot by course number (higher numbers on top)
    syllabi_pivot_modified = syllabi_pivot_modified.sort_index(
        key=lambda x: x.map(extract_course_number),
        ascending=False
    )
    
    return syllabi_pivot_modified, program_pivot

def create_heatmap(data, title, output_file):
    """
    Create and save a heatmap visualization
    """
    plt.figure(figsize=(15, 10))
    sns.heatmap(data, 
                cmap='YlOrRd',
                annot=True,
                fmt='.2f',
                cbar_kws={'label': 'Keyword Score'})
    
    plt.title(title)
    plt.xlabel('Competencies')
    plt.ylabel('Programs/Courses')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # File paths
    SYLLABI_FILE = 'data/syllabi_scores.csv'
    PROGRAM_FILE = 'data/program_scores_raw.csv'
    
    # Load and prepare data
    syllabi_data, program_data = load_and_prepare_data(SYLLABI_FILE, PROGRAM_FILE)
    
    # Create heatmaps
    create_heatmap(
        syllabi_data,
        'Course Syllabi Keyword Scores by Competency',
        'visualizations/syllabi_heatmap.png'
    )
    
    create_heatmap(
        program_data,
        'Program Keyword Scores by Competency',
        'visualizations/program_heatmap.png'
    )
    
    # Save processed data to Excel for further analysis
    with pd.ExcelWriter('data/processed_scores.xlsx') as writer:
        syllabi_data.to_excel(writer, sheet_name='Syllabi Scores')
        program_data.to_excel(writer, sheet_name='Program Scores')

if __name__ == "__main__":
    main() 