import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

query = """
WITH last AS (
    SELECT *
    FROM activity
    INNER JOIN evidence on activity.evidenceID = evidence.evidenceID
    INNER JOIN targets ON activity.targetID = targets.targetID
    INNER JOIN enhancers ON activity.enhancerID = enhancers.enhancerID
)
SELECT evidence_id, target_id, enhancer_id, enhancerName, chromosomeNumberAsReported, startAsReported, endAsReported, genomeAssemblyAsReported, organism,
       hg38Chromosome, hg38Start, hg38End, geneName, geneID, organ, tissue, cell, functionalYN,        
       methodAssay, relevantText, page, title, firstAuthor, pubYear, journal, volumePageNumber, doi, pmid, curator, comments FROM temp
EXCEPT
SELECT evidenceID, targetID, enhancerID, enhancerName, chromosomeNumberAsReported, startAsReported, endAsReported, genomeAssemblyAsReported, organism,
       hg38Chromosome, hg38Start, hg38End, geneName, geneID, organ, tissue, cell, functionalYN,        
       methodAssay, relevantText, page, title, firstAuthor, pubYear, journal, volumePageNumber, doi, pmid, curator, comments FROM last;
"""
df = pd.read_sql_query(query, conn)
cursor.execute("DROP TABLE temp;")
conn.close()

print("Query executed successfully.")
if df.empty:
    print("Test PASSED! The newly joined table and original excel are identical.")
else:
    print("Tables 'last' and 'temp' are not identical.")
    print("Differences:")
    print(df)
    
    csv_filename = "./differences.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Differences exported to {csv_filename}")