# Import required libraries
import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect(r'means_attributes.db')

# Load CSV data into Pandas DataFrame
stud_data = pd.read_csv('2023_08_28_opa_means_assessment_all_attributes.csv')
# Write the data to a sqlite table
stud_data.to_sql('attributes', conn, if_exists='replace', index=False)

# Create a cursor object
cur = conn.cursor()
# Fetch and display result
for row in cur.execute('SELECT * FROM attributes LIMIT 1'):
    print(row)
# Close connection to SQLite database
conn.close()
