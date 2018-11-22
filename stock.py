import pandas as pd
import quandl as ql
from datetime import datetime, timedelta


class StockInfo:    
    m_code_df = None
    m_day_data = dict()

    def __init__(self):
        ql.ApiConfig.api_key = open('d:\quandlapikey.txt', 'r').read()
        self.loadAllItems()
    
    def loadAllItems(self):
        self.m_code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
        
        # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        self.m_code_df.종목코드 = self.m_code_df.종목코드.map('{:06d}'.format)            
        # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
        self.m_code_df = self.m_code_df[['회사명', '종목코드']]
        # 한글로된 컬럼명을 영어로 바꿔준다.
        self.m_code_df = self.m_code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

        for code in self.m_code_df['code']:
            newDict = {code: None}
            self.m_day_data.update(newDict)

    def getCodes(self):
        return self.m_code_df['code']

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
            



    def get_daily_price(self, code, fromdate=None, todate=None):
        if todate is None:
            todate = datetime.today().strftime('%Y-%m-%d')   # 오늘 날짜

        if fromdate is None:
            fromdate = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')   # 30일 이전 날짜

        # KRX_010060
        df = ql.get_table('WIKI/PRICES', ticker = ['KRX/KRX_005930'], 
                        qopts = { 'columns': ['date', 'adj_close', 'close', 'volume'] }, 
                        date = { 'gte': '2015-12-31', 'lte': '2016-12-31' }, 
                        paginate=True)

        print(df)

        
