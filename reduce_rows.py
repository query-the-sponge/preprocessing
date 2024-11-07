import pandas as pd

# list the files
lst = ['characters_v1', 'episodes_v1']


for file in lst:
    # Load only the first 20,000 rows of the CSV file to save memory
    df = pd.read_csv(f'./output/{file}.csv', nrows=15000)

    # Save the truncated data to a new CSV file
    df.to_csv(f'./progres/{file}_cut.csv', index=False)