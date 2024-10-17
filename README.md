## Query Processing in a Data Warehouse for Steam Games Dataset

### Table of Contents

- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [Data Warehouse Design](#data-warehouse-design)
  - [Schema Diagram](#schema-diagram)
  - [Fact and Dimension Tables](#fact-and-dimension-tables)
- [ETL Pipeline](#etl-pipeline)
  - [Tools Used](#tools-used)
  - [Data Cleaning Steps](#data-cleaning-steps)
  - [Data Transformation](#data-transformation)
  - [Data Loading](#data-loading)
- [OLAP Reports](#olap-reports)
  - [Report 1: Sales Trends Over Time](#report-1-sales-trends-over-time)
  - [Report 2: Genre Popularity Analysis](#report-2-genre-popularity-analysis)
  - [Report 3: Platform Support Impact](#report-3-platform-support-impact)
  - [Report 4: Developer and Publisher Performance](#report-4-developer-and-publisher-performance)
- [Query Optimization Strategies](#query-optimization-strategies)
- [Visualization Tools](#visualization-tools)
- [Project Structure](#project-structure)
- [How to Run the Project](#how-to-run-the-project)
- [Conclusion](#conclusion)
- [References](#references)

---

## Introduction

This project involves building a data warehouse and developing an OLAP (Online Analytical Processing) application using a dataset of Steam games. The main objectives are to:

- Design a dimensional model (data warehouse) using a star schema.
- Perform ETL (Extract, Transform, Load) processes to populate the data warehouse.
- Develop an OLAP application that generates analytical reports using various OLAP operations.
- Apply query optimization strategies to improve the performance of the queries.

---

## Project Overview

We will use the `games.csv` dataset, which contains information about Steam games, including details like game names, release dates, estimated owners, prices, developers, publishers, genres, platforms, and more.

The project involves the following steps:

1. **Data Warehouse Design**: Define fact and dimension tables based on the dataset.
2. **ETL Pipeline**: Use Python with pandas for data cleaning and PeeWee ORM for database operations.
3. **OLAP Reports**: Generate reports using OLAP operations such as roll-up, drill-down, slice, dice, and pivot.
4. **Query Optimization**: Apply strategies like indexing and query restructuring to optimize query performance.
5. **Visualization**: Use appropriate tools to visualize the analytical reports.

---

## Data Warehouse Design

### Schema Diagram

![Data Warehouse Schema](schema_diagram.png) 

### Fact and Dimension Tables

#### Fact Table: `Fact_GameMetrics`

- **Measures**:
  - `Price`
  - `Discount`
  - `EstimatedOwners`
  - `PeakCCU`
  - `AveragePlaytimeForever`
  - `AveragePlaytimeTwoWeeks`
  - `MedianPlaytimeForever`
  - `MedianPlaytimeTwoWeeks`
  - `PositiveReviews`
  - `NegativeReviews`
  - `MetacriticScore`
  - `UserScore`
- **Foreign Keys**:
  - `GameID` (links to `Dim_Game`)
  - `DateID` (links to `Dim_Date`)

#### Dimension Tables

1. **Dim_Game**
   - `GameID` (Primary Key)
   - `AppID`
   - `Name`
   - `ReleaseDate`
   - `RequiredAge`
   - `AboutGame`
   - `Website`
   - `SupportURL`
   - `SupportEmail`
   - `HeaderImage`
   - `Notes`

2. **Dim_Developer**
   - `DeveloperID` (Primary Key)
   - `DeveloperName`

3. **Dim_Publisher**
   - `PublisherID` (Primary Key)
   - `PublisherName`

4. **Dim_Genre**
   - `GenreID` (Primary Key)
   - `GenreName`

5. **Dim_Category**
   - `CategoryID` (Primary Key)
   - `CategoryName`

6. **Dim_Platform**
   - `PlatformID` (Primary Key)
   - `PlatformName` (Windows, Mac, Linux)

7. **Dim_Language**
   - `LanguageID` (Primary Key)
   - `LanguageName`
   - `IsFullAudio` (Boolean)

8. **Dim_Date**
   - `DateID` (Primary Key)
   - `Date`
   - `Day`
   - `Month`
   - `Quarter`
   - `Year`
   - `Weekday`

#### Bridge Tables (for Many-to-Many Relationships)

- **Bridge_Game_Developer**
- **Bridge_Game_Publisher**
- **Bridge_Game_Genre**
- **Bridge_Game_Category**
- **Bridge_Game_Platform**
- **Bridge_Game_Language**

---

## ETL Pipeline

### Tools Used

- **Python**: Main programming language.
- **Pandas**: For data cleaning and transformation.
- **PeeWee ORM**: For interacting with the MySQL database.
- **MySQL**: Database management system.
- **MySQL Workbench**: For database administration and schema design.

### Data Cleaning Steps

1. **Load Data**: Read `games.csv` into a pandas DataFrame.

   ```python
   import pandas as pd

   df = pd.read_csv('games.csv')
   ```

2. **Handle Missing Values**:

   - Drop rows with critical missing values (e.g., `AppID`, `Name`).
   - Fill non-critical missing values with appropriate defaults.

3. **Convert Data Types**:

   - Convert `Release date` to datetime.
   - Convert numeric fields to appropriate numeric types.

4. **Handle Multi-Valued Fields**:

   - Split fields like `Developers`, `Publishers`, `Genres`, etc., into lists.
   - Trim whitespace and clean the values.

5. **Process `Estimated owners` Field**:

   - Convert ranges like `'0 - 20000'` to numeric estimates (e.g., use the midpoint).

6. **Normalize Data into Dimension Tables**:

   - Create DataFrames for each dimension table.
   - Extract unique values for dimensions.

7. **Create Bridge Tables**:

   - Establish many-to-many relationships between games and attributes.

8. **Prepare Fact Table**:

   - Extract and clean metric data.
   - Map `AppID` to `GameID`.

9. **Create `Dim_Date` Table**:

   - Extract date components for time-based analysis.

10. **Data Validation**:

    - Check for duplicates.
    - Ensure referential integrity between tables.

### Data Transformation

- **Normalization**: Separate data into fact and dimension tables according to the schema.
- **Data Type Conversion**: Ensure all data types match the schema requirements.
- **Data Enrichment**: Derive new columns (e.g., date parts in `Dim_Date`).

### Data Loading

- **Define Models with PeeWee ORM**:

  ```python
  from peewee import *

  db = MySQLDatabase('steam_dw', user='user', password='password')

  class BaseModel(Model):
      class Meta:
          database = db

  class DimGame(BaseModel):
      # Fields as per schema
      pass

  # Define other models similarly
  ```

- **Create Tables**:

  ```python
  db.connect()
  db.create_tables([DimGame, DimDeveloper, DimPublisher, DimGenre, DimCategory,
                    DimPlatform, DimLanguage, DimDate, BridgeGameDeveloper,
                    BridgeGamePublisher, BridgeGameGenre, BridgeGameCategory,
                    BridgeGamePlatform, BridgeGameLanguage, FactGameMetrics])
  ```

- **Insert Data into Tables**:

  ```python
  # Example for DimGame
  for _, row in df_game.iterrows():
      DimGame.create(**row.to_dict())
  ```

- **Load Data for All Tables**: Repeat the insertion process for each table.

---

## OLAP Reports

### Report 1: Sales Trends Over Time

- **Objective**: Analyze how game ownership estimates change over time.
- **OLAP Operations**:

  - **Roll-up**: Aggregate data from daily to monthly, quarterly, and yearly.
  - **Drill-down**: Explore data at a more granular level (e.g., from yearly to monthly).

- **Visualization**: Line chart showing estimated owners over time.

### Report 2: Genre Popularity Analysis

- **Objective**: Determine the most popular genres based on estimated owners and playtime.
- **OLAP Operations**:

  - **Slice**: Focus on specific genres.
  - **Dice**: Compare multiple genres across different platforms or age ratings.

- **Visualization**: Bar chart or heatmap of genres vs. estimated owners.

### Report 3: Platform Support Impact

- **Objective**: Assess the impact of platform availability on game popularity.
- **OLAP Operations**:

  - **Pivot**: Rearrange data to view platforms as dimensions.
  - **Drill-down**: Analyze individual game performance on each platform.

- **Visualization**: Pie chart or stacked bar chart showing distribution across platforms.

### Report 4: Developer and Publisher Performance

- **Objective**: Evaluate which developers and publishers have the most successful games.
- **OLAP Operations**:

  - **Roll-up**: Aggregate data at the developer or publisher level.

- **Visualization**: Tree map or bubble chart representing performance metrics.

---

## Query Optimization Strategies

1. **Indexing**:

   - Create indexes on frequently joined columns (e.g., foreign keys).
   - Index columns used in `WHERE` clauses.

2. **Query Restructuring**:

   - Optimize SQL queries by simplifying joins and subqueries.
   - Use appropriate SQL functions and clauses.

3. **Database Restructuring**:

   - Denormalize tables if necessary to improve read performance.
   - Partition large tables based on date or other criteria.

4. **Hardware Optimization**:

   - Ensure sufficient hardware resources (CPU, memory, disk I/O).
   - Consider using SSDs for faster data access.

---

## Visualization Tools

- **Tableau**:

  - For creating interactive dashboards and visualizations.
  - Supports advanced OLAP operations.

- **Microsoft Power BI**:

  - User-friendly interface for building reports.
  - Good for business analytics.

- **Matplotlib and Seaborn (Python Libraries)**:

  - For custom visualizations if programming is preferred.
  - Highly customizable graphs and plots.

---

## Project Structure

```
project_root/
├── data/
│   └── games.csv
├── etl/
│   ├── etl_pipeline.py
│   └── requirements.txt
├── models/
│   └── models.py
├── reports/
│   ├── report1_sales_trends.ipynb
│   ├── report2_genre_popularity.ipynb
│   ├── report3_platform_impact.ipynb
│   └── report4_developer_performance.ipynb
├── visualizations/
│   └── dashboards.twbx
├── README.md
└── schema_diagram.png
```

---

## How to Run the Project

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/steam-data-warehouse.git
   ```

2. **Navigate to Project Directory**:

   ```bash
   cd steam-data-warehouse
   ```

3. **Set Up Poetry** (optional but recommended):

   ```bash
   python -m pip install poetry
   ```

4. **Install Dependencies**:

   ```bash
   poetry install 
   ```

5. **Configure Database Connection**:

   - Update database credentials in `etl_pipeline.py` and `models.py`.

6. **Run ETL Pipeline**:

   ```bash
   python etl/etl_pipeline.py
   ```

7. **Generate Reports**:

   - Open the Jupyter notebooks in the `reports/` directory.
   - Run the cells to generate and visualize the reports.

8. **View Visualizations**:

   - Open the Tableau dashboard in `visualizations/dashboards.twbx`.

---

## Conclusion

This project demonstrates the end-to-end process of building a data warehouse, performing ETL operations, generating OLAP reports, and optimizing queries for better performance. By analyzing the Steam games dataset, we gain valuable insights into the gaming industry, such as sales trends, genre popularity, and the impact of platform support.

---

## References

- **Pandas Documentation**: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- **PeeWee ORM Documentation**: [http://docs.peewee-orm.com/](http://docs.peewee-orm.com/)
- **MySQL Documentation**: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
- **Tableau**: [https://www.tableau.com/](https://www.tableau.com/)
- **Steam Store Dataset**: *Provided in `games.csv`*

---

**Note**: This README provides an overview and instructions for replicating the project. For detailed explanations of each step, please refer to the technical report included in the project repository.
