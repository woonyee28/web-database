import pandas as pd
import sqlite3

# Connect to the SQLite database
sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)

# Define the query to find unique genome assemblies
query = """
SELECT DISTINCT genomeAssemblyAsReported
FROM enhancers;
"""

# Execute the query and fetch the unique values into a pandas DataFrame
unique_genome_assemblies = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Print the unique values
print("Unique values of genomeAssemblyAsReported:")
print(unique_genome_assemblies)
