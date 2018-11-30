import os
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta

from pandas_datareader import data as pdr
import fix_yahoo_finance as yf
from stockDB import pgDB

# PostgreSQL DB 사용
# Table : stock
#         - code, date, open, high, low, close, adj close, volume


class StockInfo:
    m_code_df = []
    #m_daily_data = dict()

    def __init__(self):
        yf.pdr_override()
        self.load_all_items()
        self.m_StockDB = pgDB()
    
    def load_all_items(self):
        df = pd.DataFrame()

        df_kospi = fdr.StockListing('KOSPI')
        df_kospi = df_kospi[['Symbol', 'Name']]
        df_kospi = df_kospi.rename(columns={'Symbol': 'code', 'Name': 'name'})
        df_kospi['type'] = '.KS'
        df = df.append(df_kospi, ignore_index=True)

        df_kosdaq = fdr.StockListing('KOSDAQ')
        df_kosdaq = df_kosdaq[['Symbol', 'Name']]
        df_kosdaq = df_kosdaq.rename(columns={'Symbol': 'code', 'Name': 'name'})
        df_kosdaq['type'] = '.KQ'
        
        df = df.append(df_kosdaq, ignore_index=True)
        self.m_code_df = df

        #for code in self.m_code_df['code']:
        #    self.m_day_data.update({code: None})

    def get_codes(self):
        return self.m_code_df['code']

    def get_code_type(self, code):
        df = self.m_code_df.loc[self.m_code_df['code'] == code]
        _type = df['type'].values[0]
        return _type

    def get_codes_len(self):
        return len(self.m_code_df)

    #def get_daily_len(self):
    #    return len(self.m_daily_data)



    def update_daily(self, code):


        #self.m_StockDB.select_daily(code)



        startdate = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')   # 90일 이전 날짜
        enddate = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')   # 1일 이전 날짜

        date = self.m_StockDB.select_last_daily_date(code)
        if not date is None:
            startdate = date.strftime('%Y-%m-%d')

        if startdate != enddate:
            df = self.get_daily_yahoo(code, startdate, enddate)
            if not df is None:
                df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume'})
                self.m_StockDB.insert_daily(code, df)

        #self.m_daily_data.update({code, df})


    def get_daily_yahoo(self, code, startdate, enddate):        
        try:
            _type = self.get_code_type(code)
            df = pdr.get_data_yahoo(code + _type, start=startdate, end=enddate, thread=20)
            return df
        except Exception as ex:
            print('[{0}] Error : {1}'.format(code, ex))
            return None





    
'''
    def get_daily(self, code, fromdate=None):
        #if todate is None:
        #    todate = datetime.today().strftime('%Y-%m-%d')   # 오늘 날짜

        if fromdate is None:
            fromdate = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')   # 90일 이전 날짜

        if self.m_day_data[code] is None:
            try:
                _type = self.get_code_type(code)
                df = pdr.get_data_yahoo(code + _type, start=fromdate, thread=20)

                df = df[['Adj Close', 'Volume']]
                df = df.rename(columns={'Adj Close': 'close', 'Volume': 'volume'})
                df[['close', 'volume']] \
                    = df[['close', 'volume']].astype(int)

                newDict = {code : df}
                self.m_day_data.update(newDict)
            except Exception as ex:
                print('[{0}] Error : {1}'.format(code, ex))
                pass

        return self.m_day_data[code]
'''




'''
    def get_daily_price(self, code, fromdate=None, todate=None):
        if todate is None:
            todate = datetime.today().strftime('%Y-%m-%d')   # 오늘 날짜

        if fromdate is None:
            fromdate = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')   # 30일 이전 날짜

        if self.m_day_data[code] is None:
            try:
                df = fdr.DataReader(code, fromdate, todate)
                df = df[['Close', 'Volume']]
                df = df.rename(columns={'Close': 'close', 'Volume': 'volume'})
                df[['close', 'volume']] \
                    = df[['close', 'volume']].astype(int)

                newDict = {code : df}
                self.m_day_data.update(newDict)
            except:
                pass

        return self.m_day_data[code]

    def get_daily_price_all(self, fromdate=None, todate=None):
        if todate is None:
            todate = datetime.today().strftime('%Y-%m-%d')   # 오늘 날짜

        if fromdate is None:
            fromdate = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')   # 30일 이전 날짜

        try:
            ticker_list = []
            for code in self.m_code_df:
                ticker_list.append(code)

            df_list = [fdr.DataReader(ticker, fromdate, todate)['Close'] for ticker in ticker_list]

            df = pd.concat(df_list, axis=1)

            df = df.dropna()

            print(df)


            #df = fdr.DataReader(code, fromdate, todate)
            #df = df[['Close', 'Volume']]
            #df = df.rename(columns={'Close': 'close', 'Volume': 'volume'})
            #df[['close', 'volume']] \
            #    = df[['close', 'volume']].astype(int)

            #newDict = {code : df}
            #self.m_day_data.update(newDict)
        except:
            pass







    def getDayData(self, code):
        if self.m_day_data[code] is None:
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

            df = pd.DataFrame()

            # 1페이지에서 10페이지의 데이터만 가져오기
            # 한페이지당 2주 (1주=5일)
            #for page in range(1, 11):
            for page in range(1, 2):
                pg_url = '{url}&page={page}'.format(url=url, page=page)
                df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
                
            # df.dropna()를 이용해 값 없는 행 제거
            df = df.dropna()

            df = df[['날짜', '종가', '시가', '고가', '저가', '거래량']]
            # 한글로 된 컬럼명을 영어로 바꿔줌
            df = df.rename(columns= {'날짜': 'date', '종가': 'close',
                                    '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
            # 데이터의 타입을 int형으로 바꿔줌
            df[['close', 'open', 'high', 'low', 'volume']] \
                = df[['close', 'open', 'high', 'low', 'volume']].astype(int)
            # 컬럼명 'date'의 타입을 date로 바꿔줌
            df['date'] = pd.to_datetime(df['date'])
            # 일자(Date)를 기준으로 오름차순 정렬
            df = df.sort_values(by=['date'], ascending=True)

            newDict = {code : df}
            self.m_day_data.update(newDict)

        return self.m_day_data[code]
'''


        
