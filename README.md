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

---

### Fact and Dimension Tables

#### Fact Table: `Fact_GameMetrics`

- **Measures**:
  - `Price`
  - `EstimatedOwners`
  - `PeakCCU`
  - `AvgPlaytimeForever`
  - `AvgPlaytimeTwoWeeks`
  - `MedianPlaytimeForever`
  - `MedianPlaytimeTwoWeeks`
  - `PositiveReviews`
  - `NegativeReviews`
  - `MetacriticScore`
  - `UserScore`
- **Foreign Keys**:
  - `GameID` (links to `Dim_Game`)

#### Dimension Tables

1. **Dim_Game**
   - `GameID` (Primary Key)
   - `AppID` (Unique)
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
   - `DeveloperName` (Unique)

3. **Dim_Publisher**
   - `PublisherID` (Primary Key)
   - `PublisherName` (Unique)

4. **Dim_Genre**
   - `GenreID` (Primary Key)
   - `GenreName` (Unique)

5. **Dim_Category**
   - `CategoryID` (Primary Key)
   - `CategoryName` (Unique)

6. **Dim_Language**
   - `LanguageID` (Primary Key)
   - `LanguageName` (Unique)

7. **Dim_Tag**
   - `TagID` (Primary Key)
   - `TagName` (Unique)

#### Bridge Tables (for Many-to-Many Relationships)

- **Bridge_Game_Developer**
  - `GameID` (links to `Dim_Game`)
  - `DeveloperID` (links to `Dim_Developer`)
  - **Indexes**: `(GameID, DeveloperID)` (unique)

- **Bridge_Game_Publisher**
  - `GameID` (links to `Dim_Game`)
  - `PublisherID` (links to `Dim_Publisher`)
  - **Indexes**: `(GameID, PublisherID)` (unique)

- **Bridge_Game_Genre**
  - `GameID` (links to `Dim_Game`)
  - `GenreID` (links to `Dim_Genre`)
  - **Indexes**: `(GameID, GenreID)` (unique)

- **Bridge_Game_Category**
  - `GameID` (links to `Dim_Game`)
  - `CategoryID` (links to `Dim_Category`)
  - **Indexes**: `(GameID, CategoryID)` (unique)

- **Bridge_Game_Language**
  - `GameID` (links to `Dim_Game`)
  - `LanguageID` (links to `Dim_Language`)
  - **Indexes**: `(GameID, LanguageID)` (unique)

- **Bridge_Game_Tag**
  - `GameID` (links to `Dim_Game`)
  - `TagID` (links to `Dim_Tag`)
  - **Indexes**: `(GameID, TagID)` (unique)

--- 

## ETL Pipeline

### Tools Used

- **Python**: Main programming language.
- **Pandas**: For data cleaning and transformation.
- **PeeWee ORM**: For interacting with the MySQL database.
- **MySQL**: Database management system.
- **MySQL Workbench**: For database administration and schema design.

### Data Cleaning and Transformation Steps

1. **Load Data**: Load the `games.json` file into a pandas DataFrame.

2. **Handle Missing Values**:
   - Identify and display missing values per column.
   - Convert `release_date` to datetime, handling any parsing errors.
   - Ensure critical fields such as `AppID` and `name` do not have missing values.

3. **Convert Data Types**:
   - Convert boolean fields (`windows`, `mac`, `linux`) to boolean types.
   - Convert numeric fields like `price`, `dlc_count`, `achievements`, etc., to appropriate numeric types, replacing invalid entries with defaults.

4. **Handle Multi-Valued Fields**:
   - Clean fields like `developers`, `publishers`, `genres`, `categories`, and `supported_languages` by ensuring they are represented as lists. 
   - Normalize and clean each value in these lists.

5. **Process `estimated_owners` Field**:
   - Split the range values in `estimated_owners` into minimum and maximum fields.
   - Calculate the midpoint as a numeric estimate.

6. **Normalize Data into Dimension Tables**:
   - Separate the cleaned data into dimension tables for `Game`, `Developer`, `Publisher`, `Genre`, `Category`, `Language`, and `Tag`.
   - Extract unique entries for each dimension to ensure a normalized schema.

7. **Create Bridge Tables**:
   - Establish many-to-many relationships between games and their attributes by creating bridge tables (e.g., `BridgeGameDeveloper`, `BridgeGamePublisher`).

8. **Prepare Fact Table**:
   - Extract and clean relevant metrics like `price`, `estimated_owners`, `playtime`, and `reviews`.
   - Ensure `AppID` maps correctly to the `GameID` in the fact table.

9. **Create `Dim_Date` Table**:
   - Derive a date dimension table with fields for `Day`, `Month`, `Year`, `Quarter`, and `Weekday` from `release_date`.
   - Ensure `DateID` is in the `YYYYMMDD` format for indexing.

10. **Data Validation**:
    - Check for duplicates across all tables.
    - Ensure referential integrity between fact and dimension tables, verifying that every foreign key matches a valid entry in its respective dimension.

### Data Transformation

- **Normalization**: Break the data into fact and dimension tables based on a snowflake schema.
- **Data Type Enforcement**: Validate that all fields have correct types, particularly numeric and date fields, to match schema requirements.
- **Data Enrichment**: Add derived fields such as date parts in `Dim_Date` and owner estimates from `estimated_owners`.
## OLAP Reports

### Report 1: Lorem Ipsum Dolor Sit

- **Objective**: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
- **OLAP Operations**:

  - **Roll-up**: Amet, consectetur adipiscing elit, sed do eiusmod tempor.
  - **Drill-down**: Lorem ipsum dolor sit amet, consectetur adipiscing elit.

- **Visualization**: Line chart showing lorem ipsum dolor sit amet.

### Report 2: Lorem Ipsum Amet

- **Objective**: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
- **OLAP Operations**:

  - **Slice**: Lorem ipsum dolor sit amet.
  - **Dice**: Dolore magna aliqua ut enim ad minim veniam.

- **Visualization**: Bar chart or heatmap of lorem ipsum dolor.

### Report 3: Dolor Amet Sit Consectetur

- **Objective**: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
- **OLAP Operations**:

  - **Pivot**: Duis aute irure dolor in reprehenderit in voluptate velit.
  - **Drill-down**: Excepteur sint occaecat cupidatat non proident.

- **Visualization**: Pie chart or stacked bar chart showing lorem ipsum.

### Report 4: Sit Amet Dolor

- **Objective**: Consectetur adipiscing elit, sed do eiusmod tempor incididunt.
- **OLAP Operations**:

  - **Roll-up**: Lorem ipsum dolor sit amet, consectetur adipiscing elit.

- **Visualization**: Tree map or bubble chart representing lorem ipsum.

---

## Query Optimization Strategies

1. **Indexing**:

   - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
   - Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

2. **Query Restructuring**:

   - Ut enim ad minim veniam, quis nostrud exercitation ullamco.
   - Dolore magna aliqua ut enim ad minim veniam.

3. **Database Restructuring**:

   - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
   - Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

4. **Hardware Optimization**:

   - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
   - Duis aute irure dolor in reprehenderit in voluptate velit.

---

## Visualization Tools

- **Tableau**:

  - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
  - Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

- **Microsoft Power BI**:

  - Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
  - Duis aute irure dolor in reprehenderit in voluptate velit.

- **Matplotlib and Seaborn (Python Libraries)**:

  - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
  - Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

---

## Project Structure

```
project_root/
├── data/
│   └── lorem.csv
├── etl/
│   ├── etl_pipeline.py
│   └── requirements.txt
├── models/
│   └── models.py
├── reports/
│   ├── report1_lorem_ipsum.ipynb
│   ├── report2_dolor_sit.ipynb
│   ├── report3_amet_consectetur.ipynb
│   └── report4_tempor_incididunt.ipynb
├── visualizations/
│   └── dashboards.twbx
├── README.md
└── schema_diagram.png
```

---

## How to Run the Project

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/lorem-ipsum-warehouse.git
   ```

2. **Navigate to Project Directory**:

   ```bash
   cd lorem-ipsum-warehouse
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

   - Update lorem ipsum credentials in `etl_pipeline.py` and `models.py`.

6. **Run ETL Pipeline**:

   ```bash
   python etl/etl_pipeline.py
   ```

---

## Conclusion

This project demonstrates lorem ipsum dolor sit amet, consectetur adipiscing elit. By analyzing the dataset, we gain valuable insights into lorem ipsum trends and more.

---

## References

- **Pandas Documentation**: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- **PeeWee ORM Documentation**: [http://docs.peewee-orm.com/](http://docs.peewee-orm.com/)
- **MySQL Documentation**: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
- **Tableau**: [https://www.tableau.com/](https://www.tableau.com/)
- **Lorem Ipsum Dataset**: *Provided in `lorem.csv`*

---
