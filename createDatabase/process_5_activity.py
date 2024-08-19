import pandas as pd
import sqlite3

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

a = f"""
ALTER TABLE temp ADD COLUMN evidence_id INTEGER;
"""

b = f"""
ALTER TABLE temp ADD COLUMN enhancer_id INTEGER;
"""

c = f"""
ALTER TABLE temp ADD COLUMN target_id INTEGER;
"""

first_query = """
UPDATE temp
SET evidence_id = (
    SELECT evidence.evidenceID
    FROM evidence
    WHERE temp.pmid = evidence.pmid AND temp.volumePageNumber = evidence.volumePageNumber AND temp.functionalYN = evidence.functionalYN AND temp.relevantText = evidence.relevantText AND temp.methodAssay = evidence.methodAssay AND temp.doi = evidence.doi AND (temp.comments = evidence.comments OR (temp.comments IS NULL AND evidence.comments IS NULL))
);
"""

second_query = f"""
UPDATE temp
SET enhancer_id = (
    SELECT e.enhancerID
    FROM enhancers e
    WHERE e.chromosomeNumberAsReported = temp.chromosomeNumberAsReported AND (e.enhancerName = temp.enhancerName OR (e.enhancerName IS NULL AND temp.enhancerName IS NULL)) AND e.startAsReported = temp.startAsReported AND e.endAsReported = temp.endAsReported AND (e.genomeAssemblyAsReported = temp.genomeAssemblyAsReported OR (e.genomeAssemblyAsReported IS NULL AND temp.genomeAssemblyAsReported IS NULL))
);
"""

third_query = f"""
UPDATE temp
SET target_id = (
    SELECT e.targetID
    FROM targets e
    WHERE (e.geneID = temp.geneID OR (e.geneID IS NULL AND temp.geneID IS NULL)) AND (e.geneName = temp.geneName OR (e.geneName IS NULL AND temp.geneName IS NULL)) AND (e.organ = temp.organ OR (e.organ IS NULL AND temp.organ IS NULL)) AND (e.tissue = temp.tissue OR (e.tissue IS NULL AND temp.tissue IS NULL)) AND (e.cell = temp.cell OR (e.cell IS NULL AND temp.cell IS NULL))
);
"""

last_query = f"""
CREATE TABLE activity (
  activityID INTEGER PRIMARY KEY AUTOINCREMENT,
  evidenceID INTEGER,
  targetID INTEGER,
  enhancerID INTEGER
);
"""

final_query = f"""
INSERT INTO activity (evidenceID, targetID, enhancerID)
SELECT evidence_id, target_id, enhancer_id
FROM temp;
"""

cursor = conn.cursor()
cursor.execute(a)
cursor.execute(b)
cursor.execute(c)
cursor.execute(first_query)
cursor.execute(second_query)
cursor.execute(third_query)
cursor.execute(last_query)
cursor.execute(final_query)

conn.commit()
conn.close()

print("Activity table created in SQLite database.")
