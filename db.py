import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# cursor.execute('''
#             CREATE TABLE users
#                (id INTEGER PRIMARY KEY,
#                user_name TEXT,
#                date_joined TEXT,
#                is_human INTEGER,
#                captcha TEXT,
#                referral_points INTEGER,
#                refered_by INTEGER,
#                chat_id INTEGER,
#                step TEXT,
#                password TEXT);
# ''')


# cursor.execute('''
#             CREATE TABLE datas
#                (id INTEGER PRIMARY KEY,
#                chat_id INTEGER,
#                welcome_text TEXT,
#                group_name TEXT
#                );
# ''')

# alter_query = "ALTER TABLE datas ADD COLUMN last_block INTEGER"
# cursor.execute(alter_query)

# cursor.execute('''
#             CREATE TABLE admins
#             (id INTEGER PRIMARY KEY);
# ''')


# cursor.execute('''
#             CREATE TABLE wallets
#                (id INTEGER PRIMARY KEY,
#                user_name TEXT,
#                date_created TEXT,
#                private_key TEXT,
#                public_key TEXT,
#                address TEXT,
#                encription TEXT);
# ''')
# cursor.execute('''ALTER TABLE wallets ADD COLUMN transactions TEXT''')
# cursor.execute('''ALTER TABLE users ADD COLUMN earned_from_referral TEXT''')
cursor.execute("""ALTER TABLE users ADD COLUMN total_bid FLOAT""")
# cursor.execute('''
#             CREATE TABLE bids
#                (id INTEGER PRIMARY KEY,
#                creator INTEGER,
#                date_created TEXT,
#                user_joined TEXT,
#                total_invested TEXT,
#                withdrawal_date TEXT,
#                chat_id INTEGER,
#                minimum_amount TEXT,
#                is_valid INTEGER);
# ''')


conn.commit()
conn.close()
# from cSRC.dbUser import AdditionalData
# data = AdditionalData(1,None,'','',0)
# data.create()
