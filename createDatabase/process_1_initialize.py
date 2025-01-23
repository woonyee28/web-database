import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

table_name = "temp"

create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    `allID` INTEGER,
    `enhancerName` TEXT,
    `chromosomeNumberAsReported` INTEGER,
    `startAsReported` INTEGER,
    `endAsReported` INTEGER,
    `genomeAssemblyAsReported` TEXT,
    `organism` TEXT,
    `hg38Chromosome` INTEGER,
    `hg38Start` INTEGER,
    `hg38End` INTEGER,
    `geneName` TEXT,
    `geneID` INTEGER,
    `organ` TEXT,
    `tissue` TEXT,
    `cell` TEXT,
    `functionalYN` TEXT,
    `methodAssay` TEXT,
    `relevantText` TEXT,
    `page` INTEGER,
    `title` TEXT,
    `firstAuthor` TEXT,
    `pubYear` INTEGER,
    `journal` TEXT,
    `volumePageNumber` TEXT,
    `doi` TEXT,
    `pmid` INTEGER,
    `curator` TEXT,
    `date` DATE,
    `comments` TEXT
)
"""
conn.execute(create_table_query)

excel_file = "./All_Curation.xlsx"
for sheet_name in ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2011','2010','2009','2008','2007','2006','2005']:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    #A check for different enhancer names but same values for all other columns
    check_columns = [col for col in df.columns if col != 'Enhancer name ' and col != 'Enhancer No.']
    df_check = df[check_columns]
    duplicates = df_check[df_check.duplicated()]
    duplicate_indices = duplicates.index
    duplicate_rows = df.loc[duplicate_indices]
    if not duplicate_rows.empty:
        print(sheet_name)
        print("Duplicate rows (excluding 'Enhancer name' and 'Enhancer No.'):\n", duplicate_rows)
    
    insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?']*len(df.columns))})"
    conn.executemany(insert_query, df.values.tolist())

add_pk_query = f"ALTER TABLE {table_name} ADD COLUMN id INTEGER"
conn.execute(add_pk_query)

populate_query = f"UPDATE {table_name} SET id = rowid"
conn.execute(populate_query)

conn.commit()
conn.close()

print("Excel data successfully exported to SQLite database.")

conn = sqlite3.connect(sqlite_db)
count_query = f"SELECT COUNT(*) FROM {table_name}"
cursor = conn.execute(count_query)
row_count = cursor.fetchone()[0]
print(f"Total number of rows in the '{table_name}' table: {row_count}")
conn.close()

