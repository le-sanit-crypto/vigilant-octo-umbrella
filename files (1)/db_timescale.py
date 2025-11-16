import psycopg2
def store_tick(symbol, ts, price, volume):
    conn = psycopg2.connect(dbname='trading', user='user', password='pass', host='localhost')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ticks (symbol, ts, price, volume) VALUES (%s, %s, %s, %s)",
        (symbol, ts, price, volume))
    conn.commit()
    cur.close()
    conn.close()