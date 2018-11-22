import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta


class StockInfo:    
    m_code_df = None
    m_day_data = dict()

    def __init__(self):
        self.load_all_items()
    
    def load_all_items(self):
        # 한국 거래소의 모든 종목 가져오기
        df = fdr.StockListing('KRX')
        df = df[['Symbol', 'Name']]
        df = df.rename(columns={'Symbol': 'code', 'Name': 'name'})
        self.m_code_df = df

        for code in self.m_code_df['code']:
            newDict = {code: None}
            self.m_day_data.update(newDict)

    def get_codes(self):
        return self.m_code_df['code']

    def get_daily_price(self, code, fromdate=None, todate=None):
        if todate is None:
            todate = datetime.today().strftime('%Y-%m-%d')   # 오늘 날짜

        if fromdate is None:
            fromdate = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')   # 30일 이전 날짜

        df = fdr.DataReader(code, '2018')

        print(df)






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
    
        
