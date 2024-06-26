import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE wallets
               (id INTEGER PRIMARY KEY,
               user_name TEXT,
               date_created TEXT,
               private_key TEXT,
               public_key TEXT,
               address TEXT,
               encription TEXT);
''')





conn.commit()
conn.close()
# from cSRC.dbUser import AdditionalData
# data = AdditionalData(1,None,'','',0)
# data.create()