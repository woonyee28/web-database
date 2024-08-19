import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

table_name = "enhancers"

create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    `enhancerID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `enhancerName` TEXT,
    `chromosomeNumberAsReported` INTEGER,
    `startAsReported` INTEGER,
    `endAsReported` INTEGER,
    `genomeAssemblyAsReported` TEXT,
    `organism` TEXT,
    `hg38Chromosome` INTEGER,
    `hg38Start` INTEGER,
    `hg38End` INTEGER,
    UNIQUE(`enhancerName`, `chromosomeNumberAsReported`, `startAsReported`, `endAsReported`, `genomeAssemblyAsReported`)
)
"""
conn.execute(create_table_query)

excel_file = "./All_Curation.xlsx"
sheet_names = ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2009','2008','2007','2006','2005']
dfs = []
for sheet_name in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df = df.iloc[:, 1:10]
    dfs.append(df)
combined_df = pd.concat(dfs, ignore_index=True)
combined_df.drop_duplicates(subset=['Chromosome number (as reported)','Enhancer name ', 'Start Position (as reported)', 'End Position (as reported)', 'Genome Assembly (as reported) (for example, hg19 or hg38, etc.)'], inplace=True)

insert_query = f"""
INSERT OR IGNORE INTO {table_name} (
    enhancerName,
    chromosomeNumberAsReported,
    startAsReported,
    endAsReported,
    genomeAssemblyAsReported,
    organism,
    hg38Chromosome,
    hg38Start,
    hg38End
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

data_to_insert = combined_df.to_records(index=False).tolist()

cursor = conn.cursor()
cursor.executemany(insert_query, data_to_insert)

conn.commit()
conn.close()

print("Enhancers table created in SQLite database.")
