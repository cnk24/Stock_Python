import psycopg2
import pandas as pd

# DB
# PostgreSQL 

class pgDB:

    def __init__(self):
        dbInfo = []
        f = open('D:/stockDB.info', 'r')
        for info in f.readlines():
            dbInfo.append(info.strip())

        self.conn_string = 'host={0} dbname={1} user={2} password={3}'.format(dbInfo[0], dbInfo[1], dbInfo[2], dbInfo[3])
        self.createTable()

    def createTable(self):
        commands = (
            """
            CREATE TABLE if not exists stock_daily (
                id SERIAL PRIMARY KEY,
                code VARCHAR(40) NOT NULL,
                date VARCHAR(40) NOT NULL,
                close VARCHAR(40) NOT NULL,
                diff VARCHAR(40),
                open VARCHAR(40),
                high VARCHAR(40),
                low VARCHAR(40),
                volume VARCHAR(40)
            )
            """,
            """
            CREATE TABLE if not exists stock_data (
                id SERIAL PRIMARY KEY,
                code VARCHAR(40) NOT NULL,
                datetime VARCHAR(40) NOT NULL,
                price VARCHAR(40) NOT NULL,
                volume VARCHAR(40)
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
            print('createTable: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()

    def select_daily_all(self):
        query = """
                SELECT * FROM stock_daily
                """

        df = pd.DataFrame()
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            
            df = df.append(rows)
            df = df.rename(columns={0: 'id', 1: 'code', 2: 'date', 3: 'close', 4: 'diff', 5: 'open', 6: 'high', 7: 'low', 8: 'volume'})
            df = df[['code', 'date', 'close', 'volume']]
            df[['close', 'volume']] \
                = df[['close', 'volume']].astype(int)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:            
            print('select_daily_all: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()

        return df

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
            # 3 : close
            # 4 : diff
            # 5 : open
            # 6 : high
            # 7 : low
            # 8 : volume
            df = df.append(rows)
            df = df.rename(columns={0: 'id', 1: 'code', 2: 'date', 3: 'close', 4: 'diff', 5: 'open', 6: 'high', 7: 'low', 8: 'volume'})
            df = df[['date', 'close', 'volume']]
            df[['close', 'volume']] \
                = df[['close', 'volume']].astype(int)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:            
            print('select_daily: {}'.format(error))
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
            date = rows[0][2] # 2: date
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print('select_last_daily_date: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()

        return date

    def insert_daily(self, code, df):
        query = """
                INSERT INTO stock_daily (date, close, diff, open, high, low, volume, code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
        df['code'] = code

        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.executemany(query, df.values)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:            
            print('insert_daily: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()

    def select_daily_lastdate(self):
        query = """
                SELECT date FROM stock_daily WHERE code = 'LAST'
                """

        date = None
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchone()
            date = rows[0]
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print('select_daily_lastdate: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()
        return date
    
    def update_daily_lastdate(self, date):
        query = None
        lastdate = self.select_daily_lastdate()
        if lastdate is None:
            query = """
                    INSERT INTO stock_daily (code, date, close) VALUES ('LAST', %s, '0')
                    """
        else:
            query = """
                    UPDATE stock_daily SET date = %s WHERE code = 'LAST'
                    """

        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query, [date])
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print('update_daily_lastdate: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()


    # 실시간 데이터 DB 저장
    def insert_real_data(self, code, price, volume):
        query = """
                INSERT INTO stock_data (code, price, volume, datetime) VALUES (%s, %s, %s, now())
                """

        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            cur.execute(query, [code, price, volume])
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:            
            print('insert_real_data: {}'.format(error))
        finally:
            if conn is not None:
                conn.close()