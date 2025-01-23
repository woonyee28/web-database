import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

table_name = "evidence"

create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    `evidenceID` INTEGER PRIMARY KEY AUTOINCREMENT,
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
    `comments` TEXT,
    UNIQUE(`relevantText`, `pmid`, `comments`, `methodAssay`,  `functionalYN`)
)
"""
conn.execute(create_table_query)

excel_file = "./All_Curation.xlsx"
sheet_names = ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2011','2010','2009','2008','2007','2006','2005']
dfs = []
for sheet_name in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df = df.iloc[:, 15:]
    if sheet_name in ['2016','2015','2014','2013','2012','2011','2010','2009']:
        df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%y',  errors='coerce')
    else:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y',  errors='coerce')
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
combined_df.drop_duplicates(subset=['Relevant Text ', 'PMID', 'Functional Y/N', 'Comments', 'Method / Assay'], inplace=True)

insert_query = f"""
INSERT OR IGNORE INTO {table_name} (
    functionalYN,
    methodAssay,
    relevantText,
    page,
    title,
    firstAuthor,
    pubYear,
    journal,
    volumePageNumber,
    doi,
    pmid,
    curator,
    date,
    comments
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

data_to_insert = combined_df.to_records(index=False).tolist()

cursor = conn.cursor()
cursor.executemany(insert_query, data_to_insert)

conn.commit()
conn.close()

print("Evidence table created in SQLite database.")
