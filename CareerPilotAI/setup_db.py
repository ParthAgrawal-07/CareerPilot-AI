import sqlite3

# Connect to database (creates it if it doesn't exist)
conn = sqlite3.connect('career.db')
c = conn.cursor()

# 1. Create Tables
c.execute('''CREATE TABLE IF NOT EXISTS streams (
                name TEXT PRIMARY KEY,
                description TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS financials (
                stream_name TEXT,
                coaching_fee INT,
                college_fee_min INT,
                college_fee_max INT,
                FOREIGN KEY(stream_name) REFERENCES streams(name)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                stream_name TEXT,
                role TEXT,
                avg_salary INT,
                FOREIGN KEY(stream_name) REFERENCES streams(name)
            )''')

# 2. Add Dummy Data
# Science
c.execute("INSERT OR IGNORE INTO streams VALUES ('Science (PCM)', 'Engineering, Tech, Physics')")
c.execute("INSERT OR IGNORE INTO financials VALUES ('Science (PCM)', 200000, 800000, 1500000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Science (PCM)', 'Software Engineer', 600000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Science (PCM)', 'Data Scientist', 800000)")

# Commerce
c.execute("INSERT OR IGNORE INTO streams VALUES ('Commerce', 'Business, Finance, Law')")
c.execute("INSERT OR IGNORE INTO financials VALUES ('Commerce', 80000, 400000, 1000000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Commerce', 'Chartered Accountant', 750000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Commerce', 'Bank Manager', 600000)")

# Arts
c.execute("INSERT OR IGNORE INTO streams VALUES ('Arts', 'Humanities, Design, Psychology')")
c.execute("INSERT OR IGNORE INTO financials VALUES ('Arts', 60000, 300000, 800000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Arts', 'Graphic Designer', 400000)")
c.execute("INSERT OR IGNORE INTO jobs VALUES ('Arts', 'Psychologist', 500000)")

conn.commit()
conn.close()
print("Database setup successfully!")