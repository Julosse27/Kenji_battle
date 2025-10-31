import sqlite3
test = 'test'
données = "Données_test//base_données.sq3"
conn = sqlite3.connect(données)
cur = conn.cursor()
cur.execute(f"create table if not exists {test}(test1 integer, test2 text)")
u = (
     (True, 'test'),
     (1, 'test'),
     (5, None)
     )
u = list(map(str, u))
i = ", "
i = i.join(u).replace('None', 'null').replace("True", '"True"')

cur.execute(f"insert into {test}(test1, test2) values {i}")

print(cur.execute(f"select name from sqlite_master").fetchall())
conn.commit()
cur.close()
conn.close()