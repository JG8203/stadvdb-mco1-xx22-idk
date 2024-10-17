import pandas as pd
import json
import os
from tqdm import tqdm

# Set pandas options for better display
pd.set_option('display.max_columns', None)

# Load the JSON file
json_file_path = 'data/games.json'
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"JSON file not found at {json_file_path}")

with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert JSON data to DataFrame
df = pd.DataFrame.from_dict(data, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'AppID'}, inplace=True)

# Display the first few rows
print("Initial DataFrame:")
print(df.head())

# Data Cleaning
print("\nMissing values per column:")
missing_values = df.isnull().sum()
print(missing_values)

# Convert 'AppID' to integer
df['AppID'] = df['AppID'].astype(int)

# Convert 'release_date' to datetime
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

# Convert numeric fields with tqdm for progress tracking
numeric_fields = [
    'required_age', 'price', 'achievements', 'recommendations',
    'user_score', 'positive', 'negative', 'average_playtime_forever',
    'average_playtime_2weeks', 'median_playtime_forever', 'median_playtime_2weeks',
    'peak_ccu', 'metacritic_score'
]
for col in tqdm(numeric_fields, desc="Converting numeric fields"):
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Handle list fields
list_fields = ['developers', 'publishers', 'genres', 'categories', 'supported_languages']
for field in list_fields:
    df[field] = df[field].apply(lambda x: x if isinstance(x, list) else [])

def clean_list(lst):
    return [item.strip() for item in lst if isinstance(item, str)]

# Clean list fields with tqdm
for field in tqdm(list_fields, desc="Cleaning list fields"):
    df[field] = df[field].apply(clean_list)

# Extract min and max owners
df[['OwnersMin', 'OwnersMax']] = df['estimated_owners'].str.replace(',', '').str.split(' - ', expand=True)
df['OwnersMin'] = pd.to_numeric(df['OwnersMin'], errors='coerce').fillna(0)
df['OwnersMax'] = pd.to_numeric(df['OwnersMax'], errors='coerce').fillna(0)
# Calculate the midpoint
df['EstimatedOwners'] = ((df['OwnersMin'] + df['OwnersMax']) / 2).astype(int)
# Drop temporary columns
df.drop(['OwnersMin', 'OwnersMax', 'estimated_owners'], axis=1, inplace=True)

# Extract relevant columns for Dim_Game
df_game = df[[
    'AppID', 'name', 'release_date', 'required_age', 'about_the_game',
    'website', 'support_url', 'support_email', 'header_image', 'notes'
]].copy()

# Rename columns to match schema
df_game.rename(columns={
    'name': 'Name',
    'release_date': 'ReleaseDate',
    'required_age': 'RequiredAge',
    'about_the_game': 'AboutGame',
    'website': 'Website',
    'support_url': 'SupportURL',
    'support_email': 'SupportEmail',
    'header_image': 'HeaderImage'
}, inplace=True)

# Explode and clean developers, publishers, genres, categories, and languages with tqdm
entities = {
    'developers': 'Developer',
    'publishers': 'Publisher',
    'genres': 'Genre',
    'categories': 'Category',
    'supported_languages': 'Language'
}

for field, entity in tqdm(entities.items(), desc="Processing entity tables"):
    df_entity = df[['AppID', field]].explode(field)
    df_entity[field] = df_entity[field].str.strip()
    unique_entities = df_entity[field].dropna().unique()
    df_entity_cleaned = pd.DataFrame(unique_entities, columns=[f'{entity}Name'])
    df_entity_cleaned.reset_index(inplace=True)
    df_entity_cleaned.rename(columns={'index': f'{entity}ID'}, inplace=True)
    globals()[f'df_{entity.lower()}'] = df_entity_cleaned

# Create bridge tables
for field, entity in tqdm(entities.items(), desc="Creating bridge tables"):
    bridge_table = df[['AppID', field]].explode(field)
    bridge_table[field] = bridge_table[field].str.strip()
    bridge_table = bridge_table.merge(globals()[f'df_{entity.lower()}'], left_on=field, right_on=f'{entity}Name', how='left')
    globals()[f'bridge_game_{entity.lower()}'] = bridge_table[['AppID', f'{entity}ID']].drop_duplicates()

# Extract relevant columns for the Fact table
df_fact = df[[
    'AppID', 'price', 'EstimatedOwners', 'peak_ccu',
    'average_playtime_forever', 'average_playtime_2weeks',
    'median_playtime_forever', 'median_playtime_2weeks',
    'positive', 'negative', 'metacritic_score', 'user_score'
]].copy()

# Rename columns to match schema
df_fact.rename(columns={
    'price': 'Price',
    'peak_ccu': 'PeakCCU',
    'average_playtime_forever': 'AvgPlaytimeForever',
    'average_playtime_2weeks': 'AvgPlaytimeTwoWeeks',
    'median_playtime_forever': 'MedianPlaytimeForever',
    'median_playtime_2weeks': 'MedianPlaytimeTwoWeeks',
    'positive': 'PositiveReviews',
    'negative': 'NegativeReviews',
    'metacritic_score': 'MetacriticScore',
    'user_score': 'UserScore'
}, inplace=True)

# Map 'AppID' to 'GameID' (assuming they are the same)
df_fact['GameID'] = df_fact['AppID']
df_fact.drop('AppID', axis=1, inplace=True)

# Ensure numeric fields in Fact table are of correct data type
numeric_fields_fact = [
    'Price', 'EstimatedOwners', 'PeakCCU', 'AvgPlaytimeForever',
    'AvgPlaytimeTwoWeeks', 'MedianPlaytimeForever', 'MedianPlaytimeTwoWeeks',
    'PositiveReviews', 'NegativeReviews', 'MetacriticScore', 'UserScore'
]

df_fact[numeric_fields_fact] = df_fact[numeric_fields_fact].apply(pd.to_numeric, errors='coerce').fillna(0)

# Convert 'GameID' to integer
df_fact['GameID'] = df_fact['GameID'].astype(int)

# Display data types
print("\nData types in Fact table:")
print(df_fact.dtypes)

# Check for duplicates in 'Dim_Game'
duplicates = df_game['AppID'].duplicated().sum()
print(f"\nDuplicate AppIDs in Dim_Game: {duplicates}")

# Ensure referential integrity (Example: All GameIDs in bridge tables exist in Dim_Game)
missing_games_in_bridge_dev = bridge_game_developer[~bridge_game_developer['AppID'].isin(df_game['AppID'])]
print(f"Missing GameIDs in Bridge_Game_Developer: {missing_games_in_bridge_dev.shape[0]}")

# Save DataFrames to CSV files
output_dir = './data/cleaned_data'
os.makedirs(output_dir, exist_ok=True)

df_game.to_csv(os.path.join(output_dir, 'dim_game.csv'), index=False)
df_developer.to_csv(os.path.join(output_dir, 'dim_developer.csv'), index=False)
df_publisher.to_csv(os.path.join(output_dir, 'dim_publisher.csv'), index=False)
df_genre.to_csv(os.path.join(output_dir, 'dim_genre.csv'), index=False)
df_category.to_csv(os.path.join(output_dir, 'dim_category.csv'), index=False)
df_language.to_csv(os.path.join(output_dir, 'dim_language.csv'), index=False)
df_fact.to_csv(os.path.join(output_dir, 'fact_game_metrics.csv'), index=False)
bridge_game_developer.to_csv(os.path.join(output_dir, 'bridge_game_developer.csv'), index=False)
bridge_game_publisher.to_csv(os.path.join(output_dir, 'bridge_game_publisher.csv'), index=False)
bridge_game_genre.to_csv(os.path.join(output_dir, 'bridge_game_genre.csv'), index=False)
bridge_game_category.to_csv(os.path.join(output_dir, 'bridge_game_category.csv'), index=False)
bridge_game_language.to_csv(os.path.join(output_dir, 'bridge_game_language.csv'), index=False)

print("\nAll data has been processed and saved successfully.")
