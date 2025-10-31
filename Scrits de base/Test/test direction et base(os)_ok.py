import os
import pyxel
import sqlite3

Données = r"données"
if not os.path.exists(Données):
    os.makedirs(Données)
données = r"données\données.sq3"
conn = sqlite3.connect(données)
cur = conn.cursor()
# cur.execute("create table a(b text)")
cur.execute('insert into a(b) values("a"), ("b")')
conn.commit()
cur.execute('select * from a')
print(list(cur))
cur.close()
conn.close()