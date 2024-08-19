import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

table_name = "targets"

create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    `targetID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `geneName` TEXT,
    `geneID` INTEGER,
    `organ` TEXT,
    `tissue` TEXT,
    `cell` TEXT,
    UNIQUE(`geneName`, `geneID`, `organ`, `tissue`, `cell`)
)
"""
conn.execute(create_table_query)

excel_file = "./All_Curation.xlsx"
sheet_names = ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2009','2008','2007','2006','2005']
dfs = []
for sheet_name in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df = df.iloc[:, 10:15]
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
combined_df.drop_duplicates(subset=['Target Gene', 'Gene ID (Target)', 'Organ', 'Tissue', 'Cell'], inplace=True)

insert_query = f"""
INSERT OR IGNORE INTO {table_name} (
    geneName,
    geneID,
    organ,
    tissue,
    cell
) VALUES (?, ?, ?, ?, ?)
"""

data_to_insert = combined_df.to_records(index=False).tolist()

cursor = conn.cursor()
new_row = (None, None, None, None, None)
cursor.executemany(insert_query, data_to_insert)
cursor.execute(insert_query, new_row)

conn.commit()
conn.close()

print("Targets table created in SQLite database.")
