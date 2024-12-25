import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_and_prepare_data(syllabi_file, program_file):
    """
    Load and prepare both CSV files for visualization
    """
    # Load the data
    syllabi_df = pd.read_csv(syllabi_file)
    program_df = pd.read_csv(program_file)
    
    # Pivot the dataframes to get competencies as columns and programs/courses as rows
    syllabi_pivot = syllabi_df.pivot(
        index='course_code',
        columns='competency',
        values='keyword_score'
    )
    
    program_pivot = program_df.pivot(
        index='program',
        columns='skill',
        values='keyword_score'
    )
    
    return syllabi_pivot, program_pivot

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