import psycopg2
import pandas as pd

# DB
# PostgreSQL 

class pgDB:

    def __init__(self):
        f = open('D:/stockDB.info', 'r')
        self.conn_string = f.readline()
        self.createTable()

    def createTable(self):
        commands = (
            """
            CREATE TABLE if not exists stock_daily (
                id SERIAL PRIMARY KEY,
                code VARCHAR(255) NOT NULL,
                date VARCHAR(255) NOT NULL,
                open VARCHAR(255),
                high VARCHAR(255),
                low VARCHAR(255),
                close VARCHAR(255) NOT NULL,
                adj_close VARCHAR(255) NOT NULL,
                volume VARCHAR(255)
            )
            """,
            """
            CREATE TABLE if not exists stock_data (
                id SERIAL PRIMARY KEY,
                code VARCHAR(255) NOT NULL,
                datetime VARCHAR(255) NOT NULL,
                price VARCHAR(255) NOT NULL,
                volume VARCHAR(255)
            )
            """
        )

        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            for command in commands:
                cur.execute(command)

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def select_daily(self, code):
        query = """
                SELECT * FROM stock_daily WHERE code = %s ORDER BY date ASC
                """

        df = pd.DataFrame()
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query, [code])
            rows = cur.fetchall()

            # 0 : id
            # 1 : code
            # 2 : date
            # 3 : open
            # 4 : high
            # 5 : low
            # 6 : close
            # 7 : adj_close
            # 8 : volume
            df = df.append(rows)
            df = df.rename(columns={'0': 'id', '1': 'code', '2': 'date', '3': 'open', '4': 'high', '5': 'low', '6': '_close_', '7': 'close', '8': 'volume'})
            df = df[['date', 'close', 'volume']]
            df[['close', 'volume']] \
                = df[['close', 'volume']].astype(int)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return df

    def select_last_daily_date(self, code):
        query = """
                SELECT * FROM stock_daily WHERE code = %s ORDER BY date DESC LIMIT 1
                """

        date = None
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query, [code])
            rows = cur.fetchall()
            date = rows['date']
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return date

    def insert_daily(self, code, df):
        query = """
                INSERT INTO stock_daily (open, high, low, close, adj_close, volume, code, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
        df['code'] = code
        df['date'] = df.index

        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.executemany(query, df.values)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
