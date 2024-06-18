import pandas as pd

# variable that can be changed (ensure that the header match the sample)
CSV_file = "sample_data_multiple_links.csv"


df = pd.read_csv(CSV_file, index_col = 0)
