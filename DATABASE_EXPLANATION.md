# InsightDB Database Explanation (Explained Like I'm 5!)

Welcome to the backend of InsightDB! Since you're learning about Databases (DBMS), this guide explains exactly what is happening under the hood when you upload data, without any confusing jargon.

## What Database are we using?
We are using **SQLite**. 
Imagine a normal database like a giant warehouse where you need a forklift and a team of workers to store boxes (that's MySQL or PostgreSQL). SQLite is like a **magic filing cabinet** that lives right inside your python project in a single file called `insightdb.db`. You don't need to install any heavy server software; it just works!

---

## Step 1: The Ingestion (Loading the Data)
*File: `backend/data_loader.py`*

When you upload a CSV file on the website, our backend reads it and immediately creates a real SQL table for it. 

We use a special command behind the scenes called `df.to_sql(...)`. This automatically looks at your CSV file, creates a table in SQLite with the same name, and inserts all the rows for you. 

---

## Step 2: The Detective (Figuring out the Schema)
*File: `backend/schema_analyzer.py`*

Before we can grade the data, we need to know what the data looks like. We run a few SQL queries to act like a detective.

### 1. Looking at the Table of Contents
```sql
PRAGMA table_info(table_name)
```
**Why we use it:** This is a special SQLite command. If a table is a book, this command reads the index. It tells us the names of all the columns (like "age", "name", "price") and what type of data they hold (like INTEGER or TEXT).

### 2. Counting the Rows
```sql
SELECT COUNT(*) FROM table_name
```
**Why we use it:** To know exactly how big the table is.

### 3. Finding Unique Items
```sql
SELECT COUNT(DISTINCT "column_name") FROM table_name
```
**Why we use it:** `DISTINCT` means "only count different ones." If we have 100 users, and this query returns 100 for the `user_id` column, it means every user has a unique ID! This helps us guess if a column is a **Primary Key**.

### 4. Finding Empty Boxes
```sql
SELECT COUNT(*) FROM table_name WHERE "column_name" IS NULL
```
**Why we use it:** `IS NULL` means "empty". We want to know how many blank spots are in the column. A good Primary Key should have 0 empty spots.

---

## Step 3: The Grader (Calculating the Trust Score)
*File: `backend/quality_engine.py`*

This is the most important part of your DBMS project. We grade the data based on how clean it is using pure SQL.

### 1. Checking for Orphans (Foreign Key Integrity)
```sql
SELECT COUNT(*) 
FROM child_table 
LEFT JOIN parent_table 
ON child_table.fk = parent_table.id
WHERE child_table.fk IS NOT NULL AND parent_table.id IS NULL
```
**Why we use it:** Imagine you have a table of `Orders` (child) and a table of `Customers` (parent). Every order needs a customer. 
A `LEFT JOIN` takes all the Orders and tries to glue them to their Customer. The `WHERE parent_table.id IS NULL` part asks: *"Show me the orders that got glued to NOTHING."* If it finds any, those orders are "orphans" (invalid foreign keys)!

### 2. Finding the Average
```sql
SELECT AVG("column_name") FROM table_name WHERE "column_name" IS NOT NULL
```
**Why we use it:** To find the middle ground of numeric data (like the average price). We ignore the empty boxes (`IS NOT NULL`).

### 3. Finding Impossible Negatives
```sql
SELECT COUNT(*) FROM table_name WHERE "column_name" < 0
```
**Why we use it:** Sometimes data is entered wrong, like a negative price or a negative age. This query counts how many rows break the rules of reality.

### 4. Finding Rare/Weird Categories
```sql
SELECT "column_name", COUNT(*) * 1.0 / TotalRows as freq 
FROM table_name 
GROUP BY "column_name" 
HAVING freq < 0.01
```
**Why we use it:** `GROUP BY` bundles all the same items together (like sorting M&Ms by color). `HAVING freq < 0.01` means *"Only show me the colors that make up less than 1% of the bag."* This finds weird typos in categories.

### 5. The Time Machine (Freshness)
```sql
SELECT MAX("date_column") FROM table_name
```
**Why we use it:** `MAX` finds the biggest or most recent date. If the most recent date is 5 years ago, we know the data is stale and we lower the Trust Score!

---

## Step 4: The Assistant (Fetching exactly what we need)
*File: `backend/app.py`*

When the AI assistant needs to look at a specific broken row to explain why it's broken, it doesn't download the whole table.

### Fetching just one row
```sql
SELECT * FROM table_name LIMIT 1 OFFSET 5
```
**Why we use it:** `LIMIT 1` means "just give me 1 row." `OFFSET 5` means "skip the first 5 rows." So this query grabs the exact 6th row instantly, saving a lot of time and memory!
