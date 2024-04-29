import pandas as pd
import sqlite3

# Step 1: Establish SQLite Connection
sqlite_db = "./createDatabase/db.sqlite3"
conn = sqlite3.connect(sqlite_db)

# Define the table name
table_name = "enhancers"

# Create the table if it doesn't exist
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    `Enhancer No.` INTEGER,
    `Enhancer name` TEXT,
    `Chromosome number (as reported)` INTEGER,
    `Start Position (as reported)` INTEGER,
    `End Position (as reported)` INTEGER,
    `Genome Assembly (as reported)` TEXT,
    `Organism` TEXT,
    `hg38 Chromosome` INTEGER,
    `hg38 Start` INTEGER,
    `hg38 End` INTEGER,
    `Target Gene` TEXT,
    `Gene ID (Target)` INTEGER,
    `Organ` TEXT,
    `Tissue` TEXT,
    `Cell` TEXT,
    `Functional Y/N` TEXT,
    `Method / Assay` TEXT,
    `Relevant Text` TEXT,
    `Page of Text` INTEGER,
    `Source Title` TEXT,
    `Source Author (first Author only)` TEXT,
    `Source Year of Publication` INTEGER,
    `Source Journal` TEXT,
    `Source Volume and Page Numbers` TEXT,
    `DOI` TEXT,
    `PMID` INTEGER,
    `Curator` TEXT,
    `Date` TEXT,
    `Comments` TEXT,
    `Sheet Name` TEXT
)
"""
conn.execute(create_table_query)

# Step 2: Iterate over each sheet in the Excel workbook
excel_file = "./createDatabase/Charmaine_Curation.xlsx"
for sheet_name in ['2016', '2015', '2014', '2013', '2012', '2009']:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df['Sheet Name'] = sheet_name

    insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?']*len(df.columns))})"
    conn.executemany(insert_query, df.values.tolist())

# Step 3: Add primary key column 'id' to the table
add_pk_query = f"ALTER TABLE {table_name} ADD COLUMN id INTEGER"
conn.execute(add_pk_query)

# Populate the 'id' column
populate_query = f"UPDATE {table_name} SET id = rowid"
conn.execute(populate_query)

conn.commit()
conn.close()

print("Excel data successfully exported to SQLite database.")
