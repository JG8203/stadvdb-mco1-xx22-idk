
from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import time  # Import the time module for measuring execution time

# Create a connection to the database
conn = create_engine("mysql+mysqlconnector://admin:password@localhost:3307/distributed_db?charset=utf8mb4")
st.title("Steam Games Data Analysis")

# Interactive year range filter
years = st.slider("Select Release Year Range", min_value=2000, max_value=2024, value=(2010, 2020), step=1)

# Report 1: Top 10 Genres by Average User Score Over Time with Genre Selector
st.header("1. Top Genres by Average User Score Over Time")

# Adding genre selection
genres_query = '''
SELECT DISTINCT gen.GenreName
FROM Dim_Genre gen
JOIN Bridge_Game_Genre bgg ON gen.GenreID = bgg.GenreID_id;
'''
# Fetch genres
available_genres = pd.read_sql(genres_query, conn)['GenreName'].tolist()

# Genre selection
selected_genres = st.multiselect("Select Genres", available_genres, default=available_genres[:5])
query1 = f'''
SELECT
    gen.GenreName,
    YEAR(g.ReleaseDate) AS ReleaseYear,
    AVG(f.UserScore) AS AvgUserScore
FROM
    Fact_GameMetrics f
    JOIN Dim_Game g ON f.GameID_id = g.GameID
    JOIN Bridge_Game_Genre bgg ON g.GameID = bgg.GameID_id
    JOIN Dim_Genre gen ON bgg.GenreID_id = gen.GenreID
WHERE
    f.UserScore > 0 AND g.ReleaseDate IS NOT NULL
    AND YEAR(g.ReleaseDate) BETWEEN {years[0]} AND {years[1]}
    AND gen.GenreName IN ({', '.join([f"'{genre}'" for genre in selected_genres])})
GROUP BY
    gen.GenreName,
    ReleaseYear
ORDER BY
    AvgUserScore DESC;
'''

start_time = time.time()  # Start the timer for the main query execution
df1 = pd.read_sql(query1, conn)
query1_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Top 10 Genres data fetched in {query1_fetch_time:.2f} seconds.")
st.write(df1)

# Visualization: Top Genres by Average User Score Over Time
st.subheader("Visualization of Top Genres by Average User Score")
if not df1.empty:
    chart_data = df1.pivot(index='ReleaseYear', columns='GenreName', values='AvgUserScore')
    st.bar_chart(chart_data)


# Report 2: Sales Performance Comparison Between Developers with Developer Selector
st.header("2. Sales Performance Comparison Between Developers")

# Adding developer selection
dev_query = '''
SELECT DISTINCT dev.DeveloperName
FROM Dim_Developer dev
JOIN Bridge_Game_Developer bgd ON dev.DeveloperID = bgd.DeveloperID_id;
'''
# Fetch available developers without timing
available_developers = pd.read_sql(dev_query, conn)['DeveloperName'].tolist()

# Developer selection
selected_developers = st.multiselect("Select Developers", available_developers, default=available_developers[:5])

# Adapting query to selected developers
query2 = f'''
SELECT
    dev.DeveloperName,
    SUM(f.EstimatedOwners) AS TotalEstimatedOwners
FROM
    Fact_GameMetrics f
    JOIN Bridge_Game_Developer bgd ON f.GameID_id = bgd.GameID_id
    JOIN Dim_Developer dev ON bgd.DeveloperID_id = dev.DeveloperID
WHERE
    dev.DeveloperName IN ({', '.join([f"'{dev}'" for dev in selected_developers])})
GROUP BY
    dev.DeveloperID
ORDER BY
    TotalEstimatedOwners DESC;
'''

start_time = time.time()  # Start the timer for the main query execution
df2 = pd.read_sql(query2, conn)
query2_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Sales performance data fetched in {query2_fetch_time:.2f} seconds.")
st.write(df2)

# Visualization: Sales Performance Comparison Between Developers
st.subheader("Top Developer Performance Visualization")
if not df2.empty:
    st.bar_chart(df2.set_index('DeveloperName'))

# Report 3: Trend Analysis of Game Prices Across Categories with Category Filter
st.header("3. Trend Analysis of Game Prices Across Categories")

# Adding category selection
categories_query = '''
SELECT DISTINCT cat.CategoryName
FROM Dim_Category cat
JOIN Bridge_Game_Category bgc ON cat.CategoryID = bgc.CategoryID_id;
'''
start_time = time.time()  # Start the timer
available_categories = pd.read_sql(categories_query, conn)['CategoryName'].tolist()
categories_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Categories fetched in {categories_fetch_time:.2f} seconds.")

selected_categories = st.multiselect("Select Categories", available_categories, default=available_categories[:5])

query3 = f'''
SELECT
    cat.CategoryName,
    YEAR(g.ReleaseDate) AS ReleaseYear,
    AVG(f.Price) AS AvgPrice
FROM
    Fact_GameMetrics f
    JOIN Dim_Game g ON f.GameID_id = g.GameID
    JOIN Bridge_Game_Category bgc ON g.GameID = bgc.GameID_id
    JOIN Dim_Category cat ON bgc.CategoryID_id = cat.CategoryID
WHERE
    f.Price > 0 AND g.ReleaseDate IS NOT NULL
    AND YEAR(g.ReleaseDate) BETWEEN {years[0]} AND {years[1]}
    AND cat.CategoryName IN ({', '.join([f"'{cat}'" for cat in selected_categories])})
GROUP BY
    cat.CategoryName,
    ReleaseYear
ORDER BY
    ReleaseYear ASC, AvgPrice DESC;
'''

start_time = time.time()  # Start the timer for query execution
df3 = pd.read_sql(query3, conn)
query3_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Game prices data fetched in {query3_fetch_time:.2f} seconds.")
st.write(df3)

# Visualization: Average Game Prices Across Categories with Interactive Filter
st.subheader("Game Prices Across Categories Over Time")
if not df3.empty:
    category = st.selectbox("Select Category", selected_categories)
    df3_filtered = df3[df3['CategoryName'] == category]
    st.line_chart(df3_filtered.set_index('ReleaseYear')['AvgPrice'])

# Report 4: Correlation Between Metacritic Scores and User Reviews with Year Filter
st.header("4. Correlation Between Metacritic Scores and User Reviews")

query4 = f'''
SELECT
    f.MetacriticScore,
    SUM(f.PositiveReviews) AS TotalPositiveReviews,
    SUM(f.NegativeReviews) AS TotalNegativeReviews
FROM
    Fact_GameMetrics f
    JOIN Dim_Game g ON f.GameID_id = g.GameID
WHERE
    f.MetacriticScore > 0 AND YEAR(g.ReleaseDate) BETWEEN {years[0]} AND {years[1]}
GROUP BY
    f.MetacriticScore
ORDER BY
    f.MetacriticScore DESC;
'''

start_time = time.time()  # Start the timer for query execution
df4 = pd.read_sql(query4, conn)
query4_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Metacritic scores data fetched in {query4_fetch_time:.2f} seconds.")
st.write(df4)

# Visualization: Metacritic Scores vs. User Reviews
st.subheader("Visualization of Metacritic Scores vs. User Reviews")
if not df4.empty:
    df4['TotalReviews'] = df4['TotalPositiveReviews'] + df4['TotalNegativeReviews']
    st.line_chart(df4.set_index('MetacriticScore')[['TotalPositiveReviews', 'TotalNegativeReviews']])

# Report 5: Language Support Impact on Game Popularity with Language Filter
st.header("5. Language Support Impact on Game Popularity")

# Adding language count range filter
language_count = st.slider("Select Number of Supported Languages", min_value=1, max_value=20, value=(1, 10))

query5 = f'''
SELECT
    Sub.LanguageCount,
    AVG(Sub.EstimatedOwners) AS AvgEstimatedOwners
FROM
    (
        SELECT
            f.GameID_id AS GameID,
            COUNT(DISTINCT bgl.LanguageID_id) AS LanguageCount,
            f.EstimatedOwners
        FROM
            Fact_GameMetrics f
            JOIN Bridge_Game_Language bgl ON f.GameID_id = bgl.GameID_id
        GROUP BY
            f.GameID_id, f.EstimatedOwners
    ) AS Sub
GROUP BY
    Sub.LanguageCount
HAVING
    Sub.LanguageCount BETWEEN {language_count[0]} AND {language_count[1]}
ORDER BY
    Sub.LanguageCount ASC;
'''

start_time = time.time()  # Start the timer for query execution
df5 = pd.read_sql(query5, conn)
query5_fetch_time = time.time() - start_time  # Calculate fetch time
st.write(f"Language support data fetched in {query5_fetch_time:.2f} seconds.")
st.write(df5)

# Visualization: Average Estimated Owners by Number of Supported Languages
st.subheader("Average Estimated Owners by Number of Supported Languages")
if not df5.empty:
    st.bar_chart(df5.set_index('LanguageCount'))
