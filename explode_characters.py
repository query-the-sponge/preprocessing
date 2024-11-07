import pandas as pd

# Read the CSV file
df = pd.read_csv("./dataset/characters.csv", delimiter=";", quotechar='"', encoding_errors='ignore')

# List columns to be exploded
lst = ['name', 'url', 'First appearance', 'Latest appearance', 'Occupation(s)',
       'Residence', 'Gender', 'Color', 'Eye color', 'Portrayer', 'Appearance',
       'Classification', 'Spouse', 'Parents', 'Children']

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


# Loop each column
for col in lst:
    # Convert the column to a list (if needed)
    df[col] = df[col].apply(safe_eval)
    # Explode the column
    df = df.explode(col).reset_index(drop=True)


# Save the result to a new CSV file
df.to_csv("./output/characters_v1.csv", index=False)