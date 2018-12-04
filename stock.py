import pandas as pd
import requests

from io import BytesIO
from datetime import datetime, timedelta
from stockDB import pgDB

import json
from pandas.io.json import json_normalize
import time


# PostgreSQL DB 사용
# Table : stock
#         - code, date, close, diff, open, high, low, volume


class StockInfo:

    def __init__(self):
        self.load_all_items()
        self.m_StockDB = pgDB()
    
    def load_all_items(self):
        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

        full_code_df = self.load_full_code()
        df = pd.merge(code_df, full_code_df, on='code')        
        self.m_code_df = df

    def load_full_code(self):
        url_tmpl = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx?bld=COM%2Ffinder_stkisu&name=form&_={}' 
        url = url_tmpl.format( int(time.time() * 1000) )
        r = requests.get(url)

        down_url = 'http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx'
        down_data = {
            'mktsel':'ALL',
            'pagePath':'/contents/COM/FinderStkIsu.jsp',
            'code': r.content,
            'geFirstCall':'Y',
        }

        r = requests.post(down_url, down_data)
        jo = json.loads(r.text)
        df = json_normalize(jo, 'block1')
        df['short_code'] = df['short_code'].str[1:]
        
        df = df[['full_code', 'marketName', 'short_code']]
        df = df.rename(columns={'short_code': 'code'})        
        return df

    def get_codes(self):
        return self.m_code_df['code']

    def get_codes_len(self):
        return len(self.m_code_df)

    def get_full_code(self, code):
        return self.m_code_df[self.m_code_df['code'] == code].iloc[0]['full_code']

    def is_last_update(self):
        today = datetime.today().strftime('%Y/%m/%d')

        lastdate = self.m_StockDB.select_daily_lastdate()
        if not lastdate is None:
            lastdatetime = datetime.strptime(lastdate, '%Y/%m/%d')
            todaytime = datetime.strptime(today, '%Y/%m/%d')
            if lastdatetime < todaytime:
                return False
        else:
            return False

        return True

    def update_last_date(self):
        today = datetime.today().strftime('%Y/%m/%d')
        self.m_StockDB.update_daily_lastdate(today)

    def update_daily(self, code):
        fromdate = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')   # 90일 이전 날짜

        todate = None
        wday = datetime.today().weekday()
        if wday == 0: # 월요일
            todate = (datetime.today() - timedelta(days=3)).strftime('%Y%m%d')
        else:
            todate = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')   # 1일 이전 날짜

        date = self.m_StockDB.select_last_daily_date(code)

        # datetime 으로 변경
        # todate 보다 작으면
        # date 1일 이후를 fromdate 로 설정        
        isGetDaily = False
        if not date is None:
            lastdatetime = datetime.strptime(date, '%Y/%m/%d')
            todatetime = datetime.strptime(todate, '%Y%m%d')
            if lastdatetime < todatetime:
                isGetDaily = True
                fromdate = (lastdatetime + timedelta(days=1)).strftime('%Y%m%d')
        else:
            isGetDaily = True

        if isGetDaily == True:
            df = self.get_daily_krx(code, fromdate, todate)
            if not df is None:
                self.m_StockDB.insert_daily(code, df)
        

    def get_daily_krx(self, code, fromdate, todate):
        try:
            full_code = self.get_full_code(code)

            # STEP 01: Generate OTP
            gen_otp_url = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx"
            gen_otp_data = {
                'name':'fileDown',
                'filetype':'csv',
                'url':'MKD/04/0402/04020100/mkd04020100t3_02',
                'isu_cd':full_code,
                'fromdate':fromdate,
                'todate':todate,
            }
            
            r = requests.post(gen_otp_url, gen_otp_data)
            content = r.content  # 리턴받은 값을 아래 요청의 입력으로 사용.
            
            # STEP 02: download
            down_url = 'http://file.krx.co.kr/download.jspx'
            down_data = {
                'code': content,
            }
            
            headers = {'Referer': 'http://marketdata.krx.co.kr'}
            r = requests.post(down_url, down_data, headers=headers)
            r.encoding = "utf-8-sig"

            df = pd.read_csv(BytesIO(r.content), header=0, thousands=',')
            df = df[['년/월/일', '종가', '대비', '시가', '고가', '저가', '거래량(주)']]
            df = df.rename(columns={'년/월/일': 'date', '종가': 'close', '대비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량(주)': 'volume'})
            return df
        except Exception as ex:
            print('[{0}] Error : {1}'.format(code, ex))
            return None    


    # 이동 평균 구하기
    def calMovingAverage(self, code, t):
        df = self.m_StockDB.select_daily(code)
        ma = df.close.ewm(span=t).mean()
        return ma

    # 상승장/하락장
    def getUpDownStock(self, code, price, day):
        ma = self.calMovingAverage(code, day)
        last_ma = ma[-1]

        state = None
        if price > last_ma:
            state = 'UP'
        else:
            state = 'DOWN'
        return state























    
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


        
