import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Step 1: Create a new table without the column to be deleted
cursor.execute(
    """
            CREATE TABLE new_bids_table 
               (id INTEGER PRIMARY KEY,
               user_name TEXT,
               date_joined TEXT,
               is_human INTEGER,
               captcha TEXT,
               referral_points INTEGER,
               refered_by INTEGER,
               chat_id INTEGER,
               step TEXT,
               password TEXT,
               earned_from_referral FLOAT);
"""
)

# Step 2: Copy data from the old table to the new table, excluding the column to be deleted
cursor.execute(
    """
    INSERT INTO new_bids_table (id,
               user_name,
               date_joined,
               is_human,
               captcha,
               referral_points,
               refered_by,
               chat_id ,
               step ,
               password ,
               earned_from_referral)
    SELECT id,user_name,date_joined,is_human,captcha,referral_points,refered_by, chat_id ,step ,password ,earned_from_referral
    FROM bids
"""
)

# Step 3: Delete or rename the old table
# To delete:
# cursor.execute('DROP TABLE my_table')
# To rename:
cursor.execute("ALTER TABLE bids RENAME TO old_bids_table")  # rename the current table

# Step 4: Rename the new table to match the old table's name
cursor.execute("ALTER TABLE new_bids_table RENAME TO bids")  # rename the old table

# Commit changes and close the database connection
conn.commit()
conn.close()
