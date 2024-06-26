import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Step 1: Create a new table without the column to be deleted
cursor.execute(
    """
            CREATE TABLE new_bids_table 
               (id INTEGER PRIMARY KEY,
               creator INTEGER,
               date_created TEXT,
               user_joined TEXT,
               total_invested FLOAT,
               withdrawal_date TEXT,
               chat_id INTEGER,
               minimum_amount FLOAT,
               is_valid INTEGER);
"""
)

# Step 2: Copy data from the old table to the new table, excluding the column to be deleted
cursor.execute(
    """
    INSERT INTO new_bids_table (id,creator,date_created,user_joined,total_invested,withdrawal_date,chat_id,minimum_amount,is_valid)
    SELECT id,creator,date_created,user_joined,total_invested,withdrawal_date,chat_id,minimum_amount,is_valid
    FROM bids
"""
)

# Step 3: Delete or rename the old table
# To delete:
# cursor.execute('DROP TABLE my_table')
# To rename:
cursor.execute("ALTER TABLE bids RENAME TO old_bids_table")

# Step 4: Rename the new table to match the old table's name
cursor.execute("ALTER TABLE new_bids_table RENAME TO bids")

# Commit changes and close the database connection
conn.commit()
conn.close()
