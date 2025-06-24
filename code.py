import requests
import json
import kis_auth as ka
import kis_ovrseastk as kb
import yaml
import pandas as pd
import sys
from ordermanager import OrderManager


#config = yaml.load("config.yaml")
#토큰 발급 kis_auth import
from evaluator import MarketSignalEvaluator

ka.auth(svr='vps')

# rt_data = kb.get_overseas_price_quot_price_detail(excd="NAS", itm_no="APLD")
# print(rt_data)    # 해외주식 현재가상세

import yfinance as yf
import pandas as pd
import numpy as np
import threading
import requests
from queue import Queue
import fear_and_greed as fg
from ordermanager import OrderManager

# ✅ RSI 계산 함수
def compute_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_trade_signal(rsi, vix, greed):
    if rsi >=30 and rsi <=70:
        return None


# ✅ 멀티스레딩 작업자 함수
def worker(ticker, all_data, vix, greed):
        try:
            print(f"📦 Processing: {ticker}")

            if ticker not in all_data.columns.get_level_values(0):
                print(f"⚠️ {ticker}: 데이터 없음")
                return

            df = all_data[ticker].dropna()
            if 'Close' not in df.columns or df['Close'].isnull().all():
                print(f"⚠️ {ticker}: 종가 없음")
                return

            close_prices = df['Close'].dropna()
            if len(close_prices) < 15:
                print(f"⚠️ {ticker}: 종가 수 부족")
                return

            rsi_series = compute_rsi(close_prices).dropna()
            if rsi_series.empty:
                return
            latest_rsi = float(rsi_series.iloc[-1])
            print(f"{ticker} Price = {close_prices[-1]}, RSI = {latest_rsi}, vix = {vix}, greed = {greed}")

            # ✅ 클래스를 사용해 판단
            evaluator = MarketSignalEvaluator(ticker=ticker, vix=vix, fgi=greed, rsi=latest_rsi)
            evaluation = evaluator.evaluate()

            if evaluation.should_buy:
                print(f"🟢 매수 조건 만족: {ticker}")
                order.place_order("buy", ticker)

            elif evaluation.should_sell:
                print(f"🔴 매도 조건 만족: {ticker}")
                order.place_order("sell", ticker)
            else:
                print("조건 만족 실패, 관망")
        except Exception as e:
                print(f"❌ [{ticker}] 처리 중 오류 발생: {e}")

# ✅ 실행 예시
order = OrderManager()
def main():
    vix = yf.download("^VIX", period="1mo", interval="1d", auto_adjust=True)
    greed = fg.get()
    latest_close = vix['Close'].iloc[-1]
    if isinstance(vix, pd.Series):
        latest_vix = latest_close.values[0]
    else:
        latest_vix = float(latest_close.iloc[0])

    print(f"VIX: {latest_vix}, Greed Index : {greed[0]}")

    # ▶️ 예제용 일부 NASDAQ 종목 (실제는 전체 NASDAQ 리스트 필요)
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "GOOGL", "META", "AMZN"]

    all_data = yf.download(
        tickers=tickers,
        period='1mo',
        interval='1d',
        group_by='ticker',
        auto_adjust=False,
        progress=False,
        threads=True  # yfinance 내부 병렬화
    )

    for ticker in tickers:
        worker(ticker, all_data, latest_vix, greed[0])

if __name__ == "__main__":
    main()
