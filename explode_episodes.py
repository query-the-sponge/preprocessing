import pandas as pd
import regex as re

# Read the CSV file
df = pd.read_csv("./dataset/episodes.csv", delimiter=";", quotechar='"', encoding_errors='ignore')

# List columns to be exploded
lst = ['Airdate', 'Animation', 'Animation Supervisor', 'Copyright year',
        'Creative', 'Episode ?', 'Guest(s)', 'Line Producer', 'Main', 'Next',
       'Previous', 'Production code', 'Running time', 'Season ?',
       'Sister episode(s)', 'Storyboard', 'Storyboard Artist(s)',
       'Supervising', 'Supervising Producer(s)', 'Technical',
       'U.S. premiere time (ET)', 'U.S. viewers (millions)', 'Writer(s)', 'title']

# Safe eval
def safe_eval(x):
    try:
        # Evaluate only if it's a list or dict; otherwise, return as is
        if isinstance(x, str) and (x.startswith("[") or x.startswith("{")):
            return eval(x)
        return x
    except Exception as e:
        print(f"Skipping value '{x}' due to error: {e}")
        return x


# Remove parentheses and only keep the main word
def clean_text(text):
    # Check if the input is a string
    if isinstance(text, str):
        # Use regex to remove all parentheses and the text within them
        cleaned_text = text.replace("\"", "")
        result = re.sub(r"\s*\([^)]*\)", "", cleaned_text)
        return result
    else:
        # If the cell is not a string, return it as-is (or return "")
        return text


# Loop each column
for col in lst:
    # Convert the column to a list (if needed)
    df[col] = df[col].apply(safe_eval)
    df[col] = df[col].apply(clean_text)
    # Explode the column
    df = df.explode(col).reset_index(drop=True)


# Special explosion for column 'characters'
# Because it doesn't have the square brackets
# Convert comma-separated strings into lists
df['characters'] = df['characters'].apply(lambda x: x.split(', '))
df['characters'] = df['characters'].apply(clean_text)

# Now use explode() to expand the lists into separate rows
df = df.explode('characters').reset_index(drop=True)


# Save the result to a new CSV file
df.to_csv("./output/episodes_v1.csv", index=False)