# EER
## Main Components

1. **Web Scraping** (`scrape.py`)
   - Extracts program information from provided URLs
   - Handles both CSV and Excel input files

2. **Program Analysis** (`nlp_label_programs.py`)
   - Analyzes program descriptions against defined competencies
   - Uses zero-shot classification for competency mapping

3. **Syllabi Analysis** (`nlp_label_syllabi.py`)
   - Processes course syllabi data
   - Maps course content to entrepreneurial competencies

4. **Visualization** (`compare_scores.py`)
   - Generates heatmaps comparing programs and syllabi
   - Provides visual representation of competency coverage

## Requirements

- Python 3.x
- Required packages: transformers, pandas, nltk, beautifulsoup4, seaborn, matplotlib

## Data Structure

The project expects the following data files:
- `data/sample_data.csv` or `data/sample_data.xlsx`: Program URLs
- `data/cocurricular_competencies.xlsx`: Competency definitions
- `data/EER_CourseSyllabi_cleaned.csv`: Course syllabi data