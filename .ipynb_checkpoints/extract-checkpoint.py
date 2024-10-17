import json
import pandas as pd
from models.models import (
    db,
    DimGame,
    DimDeveloper,
    DimPublisher,
    DimGenre,
    DimCategory,
    DimLanguage,
    DimDate,
    BridgeGameDeveloper,
    BridgeGamePublisher,
    BridgeGameGenre,
    BridgeGameCategory,
    BridgeGameLanguage,
    FactGameMetrics
)
from peewee import chunked
from datetime import datetime

def load_json_data(file_path):
    """Load the JSON data from the given file path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def prepare_dataframe(data):
    """Convert the JSON data to a pandas DataFrame."""
    # Convert the JSON dictionary to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    # Reset index to get 'AppID' as a column
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'AppID'}, inplace=True)
    return df

def clean_and_transform_data(df):
    """Clean and transform the DataFrame."""
    # Convert 'AppID' to integer
    df['AppID'] = df['AppID'].astype(int)
    
    # Convert 'release_date' to datetime
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # Handle missing values
    df.dropna(subset=['name'], inplace=True)
    
    # Fill missing numeric values with 0
    numeric_fields = [
        'required_age', 'price', 'achievements', 'recommendations',
        'user_score', 'positive', 'negative', 'average_playtime_forever',
        'average_playtime_2weeks', 'median_playtime_forever', 'median_playtime_2weeks',
        'peak_ccu', 'metacritic_score'
    ]
    
    for col in numeric_fields:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Clean multi-valued fields
    list_fields = ['developers', 'publishers', 'genres', 'categories', 'supported_languages']
    for field in list_fields:
        df[field] = df[field].apply(lambda x: [i.strip() for i in x] if isinstance(x, list) else [])
    
    # Handle 'estimated_owners' field
    df[['OwnersMin', 'OwnersMax']] = df['estimated_owners'].str.replace(',', '').str.split(' - ', expand=True)
    df['OwnersMin'] = pd.to_numeric(df['OwnersMin'], errors='coerce')
    df['OwnersMax'] = pd.to_numeric(df['OwnersMax'], errors='coerce')
    df['EstimatedOwners'] = ((df['OwnersMin'] + df['OwnersMax']) / 2).astype(int)
    df.drop(['OwnersMin', 'OwnersMax', 'estimated_owners'], axis=1, inplace=True)
    
    return df

def create_dimension_tables(df):
    """Create DataFrames for dimension tables."""
    # DimGame
    df_game = df[[
        'AppID', 'name', 'release_date', 'required_age', 'about_the_game',
        'website', 'support_url', 'support_email', 'header_image', 'notes'
    ]].copy()
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
    # Assume GameID is AppID
    df_game['GameID'] = df_game['AppID']
    
    # DimDeveloper
    df_developers = df[['AppID', 'developers']].explode('developers')
    df_developers['developers'] = df_developers['developers'].str.strip()
    unique_developers = df_developers['developers'].dropna().unique()
    df_developer = pd.DataFrame(unique_developers, columns=['DeveloperName'])
    df_developer.reset_index(inplace=True)
    df_developer.rename(columns={'index': 'DeveloperID'}, inplace=True)
    
    # DimPublisher
    df_publishers = df[['AppID', 'publishers']].explode('publishers')
    df_publishers['publishers'] = df_publishers['publishers'].str.strip()
    unique_publishers = df_publishers['publishers'].dropna().unique()
    df_publisher = pd.DataFrame(unique_publishers, columns=['PublisherName'])
    df_publisher.reset_index(inplace=True)
    df_publisher.rename(columns={'index': 'PublisherID'}, inplace=True)
    
    # DimGenre
    df_genres = df[['AppID', 'genres']].explode('genres')
    df_genres['genres'] = df_genres['genres'].str.strip()
    unique_genres = df_genres['genres'].dropna().unique()
    df_genre = pd.DataFrame(unique_genres, columns=['GenreName'])
    df_genre.reset_index(inplace=True)
    df_genre.rename(columns={'index': 'GenreID'}, inplace=True)
    
    # DimCategory
    df_categories = df[['AppID', 'categories']].explode('categories')
    df_categories['categories'] = df_categories['categories'].str.strip()
    unique_categories = df_categories['categories'].dropna().unique()
    df_category = pd.DataFrame(unique_categories, columns=['CategoryName'])
    df_category.reset_index(inplace=True)
    df_category.rename(columns={'index': 'CategoryID'}, inplace=True)
    
    # DimLanguage
    df_languages = df[['AppID', 'supported_languages']].explode('supported_languages')
    df_languages['supported_languages'] = df_languages['supported_languages'].str.strip()
    unique_languages = df_languages['supported_languages'].dropna().unique()
    df_language = pd.DataFrame(unique_languages, columns=['LanguageName'])
    df_language.reset_index(inplace=True)
    df_language.rename(columns={'index': 'LanguageID'}, inplace=True)
    # For simplicity, set IsFullAudio to False
    df_language['IsFullAudio'] = False
    
    # DimDate
    df_date = df_game[['ReleaseDate']].drop_duplicates().dropna()
    df_date['DateID'] = df_date['ReleaseDate'].dt.strftime('%Y%m%d').astype(int)
    df_date['Day'] = df_date['ReleaseDate'].dt.day
    df_date['Month'] = df_date['ReleaseDate'].dt.month
    df_date['Quarter'] = df_date['ReleaseDate'].dt.quarter
    df_date['Year'] = df_date['ReleaseDate'].dt.year
    df_date['Weekday'] = df_date['ReleaseDate'].dt.day_name()
    df_date = df_date[['DateID', 'ReleaseDate', 'Day', 'Month', 'Quarter', 'Year', 'Weekday']]
    
    return {
        'df_game': df_game,
        'df_developer': df_developer,
        'df_publisher': df_publisher,
        'df_genre': df_genre,
        'df_category': df_category,
        'df_language': df_language,
        'df_date': df_date
    }

def create_bridge_tables(df, dimension_dfs):
    """Create DataFrames for bridge tables."""
    df_game = dimension_dfs['df_game']
    df_developer = dimension_dfs['df_developer']
    df_publisher = dimension_dfs['df_publisher']
    df_genre = dimension_dfs['df_genre']
    df_category = dimension_dfs['df_category']
    df_language = dimension_dfs['df_language']
    
    # BridgeGameDeveloper
    df_developers = df[['AppID', 'developers']].explode('developers')
    df_developers['developers'] = df_developers['developers'].str.strip()
    df_developers = df_developers.dropna()
    df_developers = df_developers.merge(df_developer, left_on='developers', right_on='DeveloperName', how='left')
    bridge_game_developer = df_developers[['AppID', 'DeveloperID']].drop_duplicates()
    bridge_game_developer.rename(columns={'AppID': 'GameID'}, inplace=True)
    
    # BridgeGamePublisher
    df_publishers = df[['AppID', 'publishers']].explode('publishers')
    df_publishers['publishers'] = df_publishers['publishers'].str.strip()
    df_publishers = df_publishers.dropna()
    df_publishers = df_publishers.merge(df_publisher, left_on='publishers', right_on='PublisherName', how='left')
    bridge_game_publisher = df_publishers[['AppID', 'PublisherID']].drop_duplicates()
    bridge_game_publisher.rename(columns={'AppID': 'GameID'}, inplace=True)
    
    # BridgeGameGenre
    df_genres = df[['AppID', 'genres']].explode('genres')
    df_genres['genres'] = df_genres['genres'].str.strip()
    df_genres = df_genres.dropna()
    df_genres = df_genres.merge(df_genre, left_on='genres', right_on='GenreName', how='left')
    bridge_game_genre = df_genres[['AppID', 'GenreID']].drop_duplicates()
    bridge_game_genre.rename(columns={'AppID': 'GameID'}, inplace=True)
    
    # BridgeGameCategory
    df_categories = df[['AppID', 'categories']].explode('categories')
    df_categories['categories'] = df_categories['categories'].str.strip()
    df_categories = df_categories.dropna()
    df_categories = df_categories.merge(df_category, left_on='categories', right_on='CategoryName', how='left')
    bridge_game_category = df_categories[['AppID', 'CategoryID']].drop_duplicates()
    bridge_game_category.rename(columns={'AppID': 'GameID'}, inplace=True)
    
    # BridgeGameLanguage
    df_languages = df[['AppID', 'supported_languages']].explode('supported_languages')
    df_languages['supported_languages'] = df_languages['supported_languages'].str.strip()
    df_languages = df_languages.dropna()
    df_languages = df_languages.merge(df_language, left_on='supported_languages', right_on='LanguageName', how='left')
    bridge_game_language = df_languages[['AppID', 'LanguageID']].drop_duplicates()
    bridge_game_language.rename(columns={'AppID': 'GameID'}, inplace=True)
    
    return {
        'bridge_game_developer': bridge_game_developer,
        'bridge_game_publisher': bridge_game_publisher,
        'bridge_game_genre': bridge_game_genre,
        'bridge_game_category': bridge_game_category,
        'bridge_game_language': bridge_game_language
    }

def prepare_fact_table(df, dimension_dfs):
    """Prepare the fact table DataFrame."""
    df_fact = df[[
        'AppID', 'price', 'EstimatedOwners', 'peak_ccu',
        'average_playtime_forever', 'average_playtime_2weeks',
        'median_playtime_forever', 'median_playtime_2weeks',
        'positive', 'negative', 'metacritic_score', 'user_score'
    ]].copy()
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
    # Map 'AppID' to 'GameID'
    df_fact['GameID'] = df_fact['AppID']
    df_fact.drop('AppID', axis=1, inplace=True)
    # Map 'ReleaseDate' to 'DateID'
    df_game = dimension_dfs['df_game']
    df_date = dimension_dfs['df_date']
    df_fact = df_fact.merge(df_game[['GameID', 'ReleaseDate']], on='GameID', how='left')
    df_fact = df_fact.merge(df_date[['DateID', 'ReleaseDate']], on='ReleaseDate', how='left')
    df_fact.drop('ReleaseDate', axis=1, inplace=True)
    # Fill missing DateID with a default value or drop
    df_fact['DateID'] = df_fact['DateID'].fillna(0).astype(int)
    # Ensure numeric fields are properly typed
    numeric_fields = [
        'Price', 'EstimatedOwners', 'PeakCCU', 'AvgPlaytimeForever',
        'AvgPlaytimeTwoWeeks', 'MedianPlaytimeForever', 'MedianPlaytimeTwoWeeks',
        'PositiveReviews', 'NegativeReviews', 'MetacriticScore', 'UserScore'
    ]
    df_fact[numeric_fields] = df_fact[numeric_fields].apply(pd.to_numeric, errors='coerce').fillna(0)
    return df_fact

def insert_data_into_db(dimension_dfs, bridge_dfs, df_fact):
    """Insert data into the MySQL database using Peewee ORM."""
    with db.atomic():
        # Insert into DimGame
        games = dimension_dfs['df_game'].to_dict(orient='records')
        for batch in chunked(games, 100):
            DimGame.insert_many(batch, fields=[
                DimGame.GameID, DimGame.Name, DimGame.ReleaseDate, DimGame.RequiredAge,
                DimGame.AboutGame, DimGame.Website, DimGame.SupportURL,
                DimGame.SupportEmail, DimGame.HeaderImage, DimGame.Notes
            ]).on_conflict_ignore().execute()
        
        # Insert into DimDeveloper
        developers = dimension_dfs['df_developer'].to_dict(orient='records')
        for batch in chunked(developers, 100):
            DimDeveloper.insert_many(batch, fields=[
                DimDeveloper.DeveloperID, DimDeveloper.DeveloperName
            ]).on_conflict_ignore().execute()
        
        # Insert into DimPublisher
        publishers = dimension_dfs['df_publisher'].to_dict(orient='records')
        for batch in chunked(publishers, 100):
            DimPublisher.insert_many(batch, fields=[
                DimPublisher.PublisherID, DimPublisher.PublisherName
            ]).on_conflict_ignore().execute()
        
        # Insert into DimGenre
        genres = dimension_dfs['df_genre'].to_dict(orient='records')
        for batch in chunked(genres, 100):
            DimGenre.insert_many(batch, fields=[
                DimGenre.GenreID, DimGenre.GenreName
            ]).on_conflict_ignore().execute()
        
        # Insert into DimCategory
        categories = dimension_dfs['df_category'].to_dict(orient='records')
        for batch in chunked(categories, 100):
            DimCategory.insert_many(batch, fields=[
                DimCategory.CategoryID, DimCategory.CategoryName
            ]).on_conflict_ignore().execute()
        
        # Insert into DimLanguage
        languages = dimension_dfs['df_language'].to_dict(orient='records')
        for batch in chunked(languages, 100):
            DimLanguage.insert_many(batch, fields=[
                DimLanguage.LanguageID, DimLanguage.LanguageName, DimLanguage.IsFullAudio
            ]).on_conflict_ignore().execute()
        
        # Insert into DimDate
        dates = dimension_dfs['df_date'].to_dict(orient='records')
        for batch in chunked(dates, 100):
            DimDate.insert_many(batch, fields=[
                DimDate.DateID, DimDate.Date, DimDate.Day, DimDate.Month,
                DimDate.Quarter, DimDate.Year, DimDate.Weekday
            ]).on_conflict_ignore().execute()
        
        # Insert into Bridge Tables
        # BridgeGameDeveloper
        bridge_game_developer = bridge_dfs['bridge_game_developer'].to_dict(orient='records')
        for batch in chunked(bridge_game_developer, 100):
            BridgeGameDeveloper.insert_many(batch, fields=[
                BridgeGameDeveloper.GameID, BridgeGameDeveloper.DeveloperID
            ]).on_conflict_ignore().execute()
        
        # BridgeGamePublisher
        bridge_game_publisher = bridge_dfs['bridge_game_publisher'].to_dict(orient='records')
        for batch in chunked(bridge_game_publisher, 100):
            BridgeGamePublisher.insert_many(batch, fields=[
                BridgeGamePublisher.GameID, BridgeGamePublisher.PublisherID
            ]).on_conflict_ignore().execute()
        
        # BridgeGameGenre
        bridge_game_genre = bridge_dfs['bridge_game_genre'].to_dict(orient='records')
        for batch in chunked(bridge_game_genre, 100):
            BridgeGameGenre.insert_many(batch, fields=[
                BridgeGameGenre.GameID, BridgeGameGenre.GenreID
            ]).on_conflict_ignore().execute()
        
        # BridgeGameCategory
        bridge_game_category = bridge_dfs['bridge_game_category'].to_dict(orient='records')
        for batch in chunked(bridge_game_category, 100):
            BridgeGameCategory.insert_many(batch, fields=[
                BridgeGameCategory.GameID, BridgeGameCategory.CategoryID
            ]).on_conflict_ignore().execute()
        
        # BridgeGameLanguage
        bridge_game_language = bridge_dfs['bridge_game_language'].to_dict(orient='records')
        for batch in chunked(bridge_game_language, 100):
            BridgeGameLanguage.insert_many(batch, fields=[
                BridgeGameLanguage.GameID, BridgeGameLanguage.LanguageID
            ]).on_conflict_ignore().execute()
        
        # Insert into FactGameMetrics
        facts = df_fact.to_dict(orient='records')
        for batch in chunked(facts, 100):
            FactGameMetrics.insert_many(batch, fields=[
                FactGameMetrics.GameID, FactGameMetrics.DateID, FactGameMetrics.Price,
                FactGameMetrics.EstimatedOwners, FactGameMetrics.PeakCCU,
                FactGameMetrics.AvgPlaytimeForever, FactGameMetrics.AvgPlaytimeTwoWeeks,
                FactGameMetrics.MedianPlaytimeForever, FactGameMetrics.MedianPlaytimeTwoWeeks,
                FactGameMetrics.PositiveReviews, FactGameMetrics.NegativeReviews,
                FactGameMetrics.MetacriticScore, FactGameMetrics.UserScore
            ]).on_conflict_ignore().execute()

def main():
    # Load data
    data = load_json_data('data/games.json')
    
    # Prepare DataFrame
    df = prepare_dataframe(data)
    
    # Clean and transform data
    df = clean_and_transform_data(df)
    
    # Create dimension tables
    dimension_dfs = create_dimension_tables(df)
    
    # Create bridge tables
    bridge_dfs = create_bridge_tables(df, dimension_dfs)
    
    # Prepare fact table
    df_fact = prepare_fact_table(df, dimension_dfs)
    
    # Insert data into the database
    insert_data_into_db(dimension_dfs, bridge_dfs, df_fact)
    
    print("ETL process completed successfully.")

if __name__ == '__main__':
    main()

