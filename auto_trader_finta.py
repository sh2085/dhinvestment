import requests
import json
import pandas as pd
from finta import TA
import telegram
import time

class AutoTrader:
    def __init__(self, app_key, app_secret, telegram_token, telegram_chat_id, account_no, selected_stocks):
        self.APP_KEY = app_key
        self.APP_SECRET = app_secret
        self.ACCOUNT_NO = account_no
        self.selected_stocks = selected_stocks
        self.BASE_URL = "https://openapi.koreainvestment.com:9443"
        self.HEADER = {}
        
        self.telegram_bot = telegram.Bot(token=telegram_token)
        self.telegram_chat_id = telegram_chat_id

        self.ACCESS_TOKEN = self.get_access_token()
        self.prepare_header()

    def get_access_token(self):
        url = f"{self.BASE_URL}/oauth2/tokenP"
        headers = {"Content-Type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.APP_KEY,
            "appsecret": self.APP_SECRET
        }
        print(body)
        res = requests.post(url, headers=headers, data=json.dumps(body))
        print("토큰 발급 응답:", res.text)
        return res.json()['access_token']

    def prepare_header(self):
        self.HEADER = {
            "authorization": f"Bearer {self.ACCESS_TOKEN}",
            "appkey": self.APP_KEY,
            "appsecret": self.APP_SECRET,
            "tr_id": "TTTS3012R",
            "tr_cont": "N"
        }

    def send_telegram_message(self, msg):
        self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=msg)

    def check_balance(self):
        url = f"{self.BASE_URL}/uapi/overseas-stock/v1/trading/inquire-balance"
        params = {
            "CANO": self.ACCOUNT_NO,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": "NAS",
            "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }
        print(f"잔고 조회 요청: {params}")
        print(f"headers: {self.HEADER}")
        res = requests.get(url, headers=self.HEADER, params=params)
        print("응답 상태코드:", res.status_code)
        print("응답 본문:", res.text)
        data = res.json()
        print(f"잔고 조회 결과: {data}")
        usd_cash = float(data['output1']['cash_usd'])
        print(f"USD 잔고: ${usd_cash:.2f}")
        return usd_cash

    def get_daily_ohlcv(self, symbol):
        params = {
            "AUTH": "",
            "EXCD": "NAS",
            "SYMB": symbol,
            "period": "D",
            "count": "100"
        }
        url = f"{self.BASE_URL}/overseas-price/v1/dailyprice"
        res = requests.get(url, headers=self.HEADER, params=params)
        data = res.json()['output2']
        df = pd.DataFrame(data)
        df['close'] = df['clos'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['open'] = df['open'].astype(float)
        return df[['open','high','low','close']]

    def add_indicators(self, df):
        df['EMA5'] = TA.EMA(df, 5)
        df['EMA20'] = TA.EMA(df, 20)
        bb = TA.BBANDS(df)
        df['BB_upper'] = bb['BB_UPPER']
        df['BB_lower'] = bb['BB_LOWER']
        df['BB_width'] = df['BB_UPPER'] - df['BB_LOWER']
        df['RSI'] = TA.RSI(df)
        return df

    def generate_signals(self, df):
        min_bandwidth = 0.01 * df['close']
        df['long_signal'] = (
            (df['EMA5'] > df['EMA20']) &
            (df['close'] > df['BB_upper']) &
            (df['RSI'] < 70) &
            (df['BB_width'] > min_bandwidth)
        )
        df['short_signal'] = (
            (df['EMA5'] < df['EMA20']) &
            (df['close'] < df['BB_lower']) &
            (df['RSI'] > 30) &
            (df['BB_width'] > min_bandwidth)
        )
        return df

    def place_order(self, symbol, qty, side="buy"):
        url = f"{self.BASE_URL}/overseas-stock/v1/trading/order"
        body = {
            "CANO": self.ACCOUNT_NO,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": "NAS",
            "PDNO": symbol,
            "ORD_QTY": str(qty),
            "OVRS_ORD_UNPR": "MKT",
            "ORD_SVR_DVSN_CD": "0",
            "BUY_SELL_DVSN_CD": "01" if side == "buy" else "02",
            "CURRENCY_CD": "USD"
        }
        res = requests.post(url, headers=self.HEADER, data=json.dumps(body))
        return res.json()

    def run(self):
        for stock in self.selected_stocks:
            try:
                cash_usd = self.check_balance()
                if cash_usd < 100:
                    self.send_telegram_message(f"🚫 주문불가: {stock} - USD 잔고 부족 (${cash_usd:.2f})")
                    continue

                df = self.get_daily_ohlcv(stock)
                df = self.add_indicators(df)
                df = self.generate_signals(df)
                latest = df.iloc[-1]

                if latest['long_signal']:
                    order_res = self.place_order(stock, 1, side="buy")
                    self.send_telegram_message(f"📈 {stock} 매수: {order_res}")
                elif latest['short_signal']:
                    order_res = self.place_order(stock, 1, side="sell")
                    self.send_telegram_message(f"📉 {stock} 매도: {order_res}")
                else:
                    print(f"😴 {stock} 신호 없음")
            except Exception as e:
                self.send_telegram_message(f"⚠️ {stock} 처리 에러: {str(e)}")
                print(f"Error processing {stock}: {e}")
            time.sleep(5)
