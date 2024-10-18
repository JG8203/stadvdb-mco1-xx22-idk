from sqlalchemy import create_engine
import streamlit as st
import pandas as pd

conn = create_engine("mysql+pymysql://admin:password@localhost/games?charset=utf8mb4")

st.title("Game Data Reports")

st.header("1. Total Estimated Owners per Genre")

query1 = '''
SELECT
    g.GenreName,
    SUM(f.EstimatedOwners) AS TotalEstimatedOwners
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Genre bgg ON dg.GameID = bgg.GameID_id
    JOIN Dim_Genre g ON bgg.GenreID_id = g.GenreID
GROUP BY
    g.GenreName
ORDER BY
    TotalEstimatedOwners DESC
'''

df1 = pd.read_sql(query1, conn)
st.bar_chart(df1.set_index('GenreName'))

# 2. Average User Score per Developer
st.header("2. Average User Score per Developer")

query2 = '''
SELECT
    d.DeveloperName,
    AVG(f.UserScore) AS AverageUserScore
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Developer bgd ON dg.GameID = bgd.GameID_id
    JOIN Dim_Developer d ON bgd.DeveloperID_id = d.DeveloperID
GROUP BY
    d.DeveloperName
HAVING
    COUNT(f.UserScore) >= 5
ORDER BY
    AverageUserScore DESC
LIMIT 20
'''

df2 = pd.read_sql(query2, conn)
st.write(df2)

# 3. Total Positive and Negative Reviews per Year
st.header("3. Total Positive and Negative Reviews per Year")

query3 = '''
SELECT
    YEAR(dg.ReleaseDate) AS ReleaseYear,
    SUM(f.PositiveReviews) AS TotalPositiveReviews,
    SUM(f.NegativeReviews) AS TotalNegativeReviews
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
WHERE
    dg.ReleaseDate IS NOT NULL
GROUP BY
    ReleaseYear
ORDER BY
    ReleaseYear
'''

df3 = pd.read_sql(query3, conn)
df3 = df3.dropna()
st.line_chart(df3.set_index('ReleaseYear'))

# 4. Average Price per Genre
st.header("4. Average Price per Genre")

query4 = '''
SELECT
    g.GenreName,
    AVG(f.Price) AS AveragePrice
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Genre bgg ON dg.GameID = bgg.GameID_id
    JOIN Dim_Genre g ON bgg.GenreID_id = g.GenreID
WHERE
    f.Price IS NOT NULL
GROUP BY
    g.GenreName
ORDER BY
    AveragePrice DESC
'''

df4 = pd.read_sql(query4, conn)
st.bar_chart(df4.set_index('GenreName'))

# 5. Total Estimated Owners per Language
st.header("5. Total Estimated Owners per Language")

query5 = '''
SELECT
    l.LanguageName,
    SUM(f.EstimatedOwners) AS TotalEstimatedOwners
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Language bgl ON dg.GameID = bgl.GameID_id
    JOIN Dim_Language l ON bgl.LanguageID_id = l.LanguageID
GROUP BY
    l.LanguageName
ORDER BY
    TotalEstimatedOwners DESC
LIMIT 10
'''

df5 = pd.read_sql(query5, conn)
st.bar_chart(df5.set_index('LanguageName'))

# 6. Top 10 Publishers by Total Estimated Owners
st.header("6. Top 10 Publishers by Total Estimated Owners")

query6 = '''
SELECT
    p.PublisherName,
    SUM(f.EstimatedOwners) AS TotalEstimatedOwners
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Publisher bgp ON dg.GameID = bgp.GameID_id
    JOIN Dim_Publisher p ON bgp.PublisherID_id = p.PublisherID
GROUP BY
    p.PublisherName
ORDER BY
    TotalEstimatedOwners DESC
LIMIT 10
'''

df6 = pd.read_sql(query6, conn)
st.write(df6)

# 7. Median Playtime Forever per Genre
st.header("7. Median Playtime Forever per Genre")

query7 = '''
WITH RankedPlaytimes AS (
    SELECT 
        g.GenreName,
        f.MedianPlaytimeForever,
        ROW_NUMBER() OVER (PARTITION BY g.GenreName ORDER BY f.MedianPlaytimeForever) as row_num,
        COUNT(*) OVER (PARTITION BY g.GenreName) as total_rows
    FROM 
        Fact_GameMetrics f
        JOIN Dim_Game dg ON f.GameID_id = dg.GameID
        JOIN Bridge_Game_Genre bgg ON dg.GameID = bgg.GameID_id
        JOIN Dim_Genre g ON bgg.GenreID_id = g.GenreID
    WHERE 
        f.MedianPlaytimeForever IS NOT NULL
)
SELECT 
    GenreName,
    AVG(MedianPlaytimeForever) as MedianPlaytime
FROM 
    RankedPlaytimes
WHERE 
    row_num IN (FLOOR((total_rows + 1)/2), CEIL((total_rows + 1)/2))
GROUP BY 
    GenreName
ORDER BY 
    MedianPlaytime DESC
'''

df7 = pd.read_sql(query7, conn)
st.bar_chart(df7.set_index('GenreName'))

# 8. Metacritic Score Distribution by Year
st.header("8. Metacritic Score Distribution by Year")

query8 = '''
SELECT
    YEAR(dg.ReleaseDate) AS ReleaseYear,
    AVG(f.MetacriticScore) AS AverageMetacriticScore,
    MIN(f.MetacriticScore) AS MinMetacriticScore,
    MAX(f.MetacriticScore) AS MaxMetacriticScore
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
WHERE
    f.MetacriticScore IS NOT NULL AND dg.ReleaseDate IS NOT NULL
GROUP BY
    ReleaseYear
ORDER BY
    ReleaseYear
'''

df8 = pd.read_sql(query8, conn)
st.line_chart(df8.set_index('ReleaseYear'))

# 9. Number of Games Released per Developer Over Time
st.header("9. Number of Games Released per Developer Over Time")

developer = st.selectbox("Select a Developer", options=[])

query9 = f'''
SELECT
    YEAR(dg.ReleaseDate) AS ReleaseYear,
    COUNT(*) AS NumberOfGames
FROM
    Dim_Game dg
    JOIN Bridge_Game_Developer bgd ON dg.GameID = bgd.GameID_id
    JOIN Dim_Developer d ON bgd.DeveloperID_id = d.DeveloperID
WHERE
    dg.ReleaseDate IS NOT NULL AND d.DeveloperName = '{developer}'
GROUP BY
    ReleaseYear
ORDER BY
    ReleaseYear
'''

df9 = pd.read_sql("SELECT DeveloperName FROM Dim_Developer", conn)
developer_list = df9['DeveloperName'].tolist()
developer = st.selectbox("Select a Developer", options=developer_list)

if developer:
    df9 = pd.read_sql(query9, conn)
    st.line_chart(df9.set_index('ReleaseYear'))

# 10. Average Positive Review Rate per Genre
st.header("10. Average Positive Review Rate per Genre")

query10 = '''
SELECT
    g.GenreName,
    AVG(f.PositiveReviews / (f.PositiveReviews + f.NegativeReviews)) AS AveragePositiveReviewRate
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Genre bgg ON dg.GameID = bgg.GameID_id
    JOIN Dim_Genre g ON bgg.GenreID_id = g.GenreID
WHERE
    (f.PositiveReviews + f.NegativeReviews) > 0
GROUP BY
    g.GenreName
ORDER BY
    AveragePositiveReviewRate DESC
'''

df10 = pd.read_sql(query10, conn)
st.bar_chart(df10.set_index('GenreName'))

# 11. Top Tags by Total Estimated Owners
st.header("11. Top Tags by Total Estimated Owners")

query11 = '''
SELECT
    t.TagName,
    SUM(f.EstimatedOwners) AS TotalEstimatedOwners
FROM
    Fact_GameMetrics f
    JOIN Dim_Game dg ON f.GameID_id = dg.GameID
    JOIN Bridge_Game_Tag bgt ON dg.GameID = bgt.GameID_id
    JOIN Dim_Tag t ON bgt.TagID_id = t.TagID
GROUP BY
    t.TagName
ORDER BY
    TotalEstimatedOwners DESC
LIMIT 10
'''

df11 = pd.read_sql(query11, conn)
st.bar_chart(df11.set_index('TagName'))

# 13. Average Playtime per Price Category
st.header("13. Average Playtime per Price Category")

query13 = '''
SELECT
    CASE
        WHEN f.Price = 0 THEN 'Free'
        WHEN f.Price > 0 AND f.Price <= 10 THEN '$0 - $10'
        WHEN f.Price > 10 AND f.Price <= 30 THEN '$10 - $30'
        ELSE '$30+'
    END AS PriceCategory,
    AVG(f.AvgPlaytimeForever) AS AveragePlaytime
FROM
    Fact_GameMetrics f
WHERE
    f.Price IS NOT NULL AND f.AvgPlaytimeForever IS NOT NULL
GROUP BY
    PriceCategory
ORDER BY
    PriceCategory
'''

df13 = pd.read_sql(query13, conn)
st.bar_chart(df13.set_index('PriceCategory'))

# 15. Language Distribution of Games Released per Year
st.header("15. Language Distribution of Games Released per Year")

query15 = '''
SELECT
    YEAR(dg.ReleaseDate) AS ReleaseYear,
    l.LanguageName,
    COUNT(*) AS NumberOfGames
FROM
    Dim_Game dg
    JOIN Bridge_Game_Language bgl ON dg.GameID = bgl.GameID_id
    JOIN Dim_Language l ON bgl.LanguageID_id = l.LanguageID
WHERE
    dg.ReleaseDate IS NOT NULL
GROUP BY
    ReleaseYear,
    l.LanguageName
ORDER BY
    ReleaseYear,
    NumberOfGames DESC
'''

df15 = pd.read_sql(query15, conn)

years = df15['ReleaseYear'].unique()
selected_year = st.slider("Select Year", int(years.min()), int(years.max()))

df15_year = df15[df15['ReleaseYear'] == selected_year]
st.bar_chart(df15_year.set_index('LanguageName')['NumberOfGames'])
